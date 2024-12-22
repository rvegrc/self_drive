import pandas as pd

# read data in each file with spark
def make_df_id(control:pd.DataFrame, localization:pd.DataFrame, metadata:pd.DataFrame) -> pd.DataFrame:
    '''Make a model dataframe from control, localization and metadata dataframes for a single id'''

    def find_min_max(control:pd.DataFrame, localization:pd.DataFrame):
        '''Find min and max timestamp in localization for each timestamp in control dataframe'''
        control['loclz_stamp_ns_max'] = control['stamp_ns'].apply(lambda x: localization[localization['stamp_ns'] >= x]['stamp_ns'].min())
        control['loclz_stamp_ns_min'] = control['stamp_ns'].apply(lambda x: localization[localization['stamp_ns'] < x]['stamp_ns'].max())
        control['loclz_stamp_ns_min'] = control['loclz_stamp_ns_min'].apply(lambda x: localization['stamp_ns'].min() if pd.isnull(x) else x)
        control_2m = control.copy()
        control_2m.rename(columns={'stamp_ns':'ctrl_stamp_ns'}, inplace=True)
        return control_2m

    def merge_min_max(control_2m:pd.DataFrame, localization:pd.DataFrame):
        '''Merge min and max timestamp in localization for each timestamp in control dataframe'''
        control_3m = (control_2m.merge(localization, left_on='loclz_stamp_ns_max', right_on='stamp_ns', how='left', suffixes=('', '_max'))
                    .merge(localization, left_on='loclz_stamp_ns_min', right_on='stamp_ns', how='left', suffixes=('', '_min'))
        )
        control_3m.rename(columns={'x':'x_max'
                                ,'y':'y_max'
                                ,'z':'z_max'
                                ,'roll':'roll_max'
                                ,'pitch':'pitch_max'
                                ,'yaw':'yaw_max'
                                ,'stamp_ns':'stamp_ns_max'
                    }, inplace=True)
        control_3m.drop(columns=['loclz_stamp_ns_max', 'loclz_stamp_ns_min'], inplace=True)
        return control_3m

    def interpolate_coords(control_3m, col_min:str, col_max:str):
        '''Interpolate values between max and min values'''
        # control_interpolated = (control_3m[['ctrl_stamp_ns', 'stamp_ns_max', 'stamp_ns_min', col_min, col_max]]
        #             .apply(lambda x: (x['ctrl_stamp_ns'] - x['stamp_ns_min']) / (x['stamp_ns_max'] - x['stamp_ns_min']) * (x[col_max] - x[col_min]) + x[col_min], axis=1)
        #             )
        # return control_interpolated
    
        control_interpolated = (control_3m[['ctrl_stamp_ns', 'stamp_ns_max', 'stamp_ns_min', col_min, col_max]]
                .apply(lambda x:
                    x[col_min] if x['stamp_ns_max'] == x['stamp_ns_min']
                    else (x['ctrl_stamp_ns'] - x['stamp_ns_min']) / (x['stamp_ns_max'] - x['stamp_ns_min']) * (x[col_max] - x[col_min]) + x[col_min], axis=1
                    )
                )
        # x = control_3m
        # print(f"stamp_ns_max {x['stamp_ns_max'].isnull().sum()}")
        # print(f"stamp_ns_min {x['stamp_ns_min'].isnull().sum()}")
        # print(f"{col_min} {x[col_min].isnull().sum()}")
        # print(f"{col_max} {x[col_max].isnull().sum()}")
        # print((x['ctrl_stamp_ns'] - x['stamp_ns_min']).isnull().sum())
        # print((x['stamp_ns_max'] - x['stamp_ns_min']).isnull().sum())
        # print((x[col_max] - x[col_min]).isnull().sum())
        # print(control_interpolated.isnull().sum())

        return control_interpolated

    def tires_to_columns_date(metadata:pd.DataFrame):
        '''Change tires column to front and rear columns and 
        convert ride_date to datetime and add year, month, day columns'''
        metadata['front_tire'] = metadata['tires'][0]
        metadata['rear_tire'] = metadata['tires'][1]
        metadata = metadata.drop(columns=['tires']).reset_index(drop=True).loc[:0]
        # convert ride_date to datetime and add year, month, day columns
        metadata['ride_date'] = pd.to_datetime(metadata['ride_date'])
        metadata['ride_year'] = metadata['ride_date'].dt.year
        metadata['ride_month'] = metadata['ride_date'].dt.month
        metadata['ride_day'] = metadata['ride_date'].dt.day
        metadata = metadata.drop(columns=['ride_date'])
        
        return metadata

    def add_metadata(control:pd.DataFrame, metadata:pd.DataFrame):
        '''Add metada to each row in control dataframe'''
        # Make a copy to avoid SettingWithCopyWarning
        control_model = control.copy()
        for col in metadata.columns:
            control_model[col] = metadata.loc[0, col]  # Set the entire column in the copy
        
        return control_model

    # find min and max timestamp in localization for each timestamp in control dataframe
    control_2m = find_min_max(control, localization)
    # merge min and max timestamp in localization for each timestamp in control dataframe
    control_3m = merge_min_max(control_2m, localization)
    
    
    coords_cols = ['x', 'y', 'z', 'roll', 'pitch', 'yaw']
    contr_cols = ['ctrl_stamp_ns', 'acceleration_level', 'steering']

    # interpolate values between max and min values
    for col in coords_cols:
        control_3m[col] = interpolate_coords(control_3m, f'{col}_min', f'{col}_max')

    # select coords and control columns
    control_interpolated = control_3m[contr_cols + coords_cols]
   
    # change tires column to front and rear columns and convert ride_date to datetime and add year, month, day columns
    metadata_m = tires_to_columns_date(metadata)
 
    clm = add_metadata(control_interpolated, metadata_m)

    # add acceleration_level and steering columns with shifts
    for col in ['acceleration_level', 'steering']:
        for i in range(1, 4):
            clm[f'{col}_shift_{i}'] = clm[col].shift(i)

    # add x, y, yaw columns with shifts
    for col in ['x', 'y', 'yaw']:
        for i in range(1, 4):
            clm[f'{col}_shift_{i}'] = clm[col].shift(i)

    # add mean last 10 values for acceleration_level and steering columns
    for col in ['acceleration_level', 'steering']:
        clm[f'{col}_last_10_mean'] = clm[col].rolling(window=10).mean()

    # add mean last 10 values for x, y, yaw columns
    for col in ['x', 'y', 'yaw']:
        clm[f'{col}_last_10_mean'] = clm[col].rolling(window=10).mean()



    return clm



def make_df_all_ids(path: str, ids: pd.Series, files: list) -> pd.DataFrame:
    '''Read data in each file, preprocess and concat files for each id, concat df for each id and save it to parquet file '''
    data = []
    for i in ids:
        for file in files:
            if file == 'control.csv':
                control = pd.read_csv(f'{path}/{i}/{file}')
            elif file == 'localization.csv':
                localization = pd.read_csv(f'{path}/{i}/{file}')
            elif file == 'metadata.json':
                metadata = pd.read_json(f'{path}/{i}/{file}')
        
       
        clm = make_df_id(control, localization, metadata)

        # add id column
        clm['id'] = i

        # clm.to_parquet(f'{tmp_data_path}/clm_{i}.parquet', index=False)
        
        data.append(clm)
        if i % 1000 == 0:
            print(f'id={i}')
    
    # Concatenate all DataFrames from the list
    data_clm = pd.concat(data, ignore_index=True)

     
    return data_clm