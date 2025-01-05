import pandas as pd

# read data in each file with spark
def union_dfs(control:pd.DataFrame, localization:pd.DataFrame, metadata:pd.DataFrame) -> pd.DataFrame:
    '''Make a interpolated dataframe from control, localization and metadata dataframes for a single id'''

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
    
        control_interpolated = (control_3m[['ctrl_stamp_ns', 'stamp_ns_max', 'stamp_ns_min', col_min, col_max]]
                .apply(lambda x:
                    x[col_min] if x['stamp_ns_max'] == x['stamp_ns_min']
                    else (x['ctrl_stamp_ns'] - x['stamp_ns_min']) / (x['stamp_ns_max'] - x['stamp_ns_min']) * (x[col_max] - x[col_min]) + x[col_min], axis=1
                    )
                )

        return control_interpolated


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
   
 
    clm = add_metadata(control_interpolated, metadata)

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