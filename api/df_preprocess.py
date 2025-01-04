
import pandas as pd
import numpy as np

import category_encoders as ce




def set_cols_for_model(train:pd.DataFrame, target:str=None):
    '''Set num and cat columns for model'''
    
    cols_checked = train.columns

    # target in [ ] because yaw hase more then one letter
    not_target = list(set(targets) - set([target]))


    # Set num columns
    control_cols = ['ctrl_stamp_ns', 'acceleration_level', 'steering']
    shift_cols = [col for col in cols_checked if '_shift' in col]
    tmp = [col for col in shift_cols for nt in not_target if f'{nt}_' in col]
    shift_cols = list(set(shift_cols) - set(tmp))

    last_10_cols = [col for col in cols_checked if 'last_10' in col]
    tmp = [col for col in last_10_cols for nt in not_target if f'{nt}_' in col]
    last_10_cols = list(set(last_10_cols) - set(tmp))

    num_cols = control_cols + shift_cols + last_10_cols

    # Set categorical columns
    cols_temp = [col for col in cols_checked if col in control_cols or 'last' in col or 'shift' in col or 'diff' in col]
    cat_cols = list(set(cols_checked) - set(cols_temp) - set(targets))


    return cat_cols, num_cols



# catboost encoder
def ctb_encoder(test:pd.DataFrame, target:str, id) -> pd.DataFrame:
    '''Encode with CatBoostEncoder categorical columns of each target test data    '''     
    # drop unnecessary columns
    test_target = test[test['id'] == id].drop(columns=['z', 'roll', 'pitch'])

    # set columns for one target
    cat_cols, num_cols = set_cols_for_model(test_target, target)

    # obsereved columns
    obs_cols = [col for col in test_target.columns if 'obs' in col] 

    
    # use only columns for one target and 'shift_1_obs' doesn't need to encode
    test_target = test_target.loc[:, cat_cols + list(set(num_cols) - set(obs_cols))]

    # fill null in target_shift column for correct work CatBoostEncoder
    test_target.fillna(value={f'{target}_shift_1': -1}, inplace=True)

    # encode categorical columns
    test_target = ce.cat_boost.CatBoostEncoder(cols=cat_cols).fit_transform(test_target, test_target[f'{target}_shift_1'])

    # del num and reminder from col names
    # train_target.columns = [col.split("__")[1] if "__" in col else col for col in train_target.columns]

    # replace -1 to nan
    test_target[f'{target}_shift_1'].replace(-1, np.nan, inplace=True)


    # add target column to the end
    test_target[target] = test[target]
 
    test_target['id_obs'] = id

    
    return test_target


def df_preprocess(test: pd.DataFrame, target: str, id: int, preprocessor_path: str) -> pd.DataFrame:
    '''Preprocess test one id_obs data for model
    cat_cols encoded with CatBoostEncoder
    num_cols transformed with PowerTransformer
   
    test - copy of test data
    '''
    
    test_id = test[test['id'] == id]

    # add target columns with shifts
    for i in range(1, 4):
        test_id[f'{target}_shift_{i}'] = test_id[target].shift(i)

    # add mean last 10 values for target columns
    test_id[f'{target}_last_10_mean'] = test_id[target].rolling(window=10).mean()

    # # add obs shift_1 column to preprocessed data
    # test_id[f'{target}_shift_1_obs'] = test_id[f'{target}_shift_1']

    # load preprocessor
    # cat_encoder = pd.read_pickle(f'{tmp_data_path}/cat_encoder_{target}.pkl')
    preprocessor = pd.read_pickle(f'{preprocessor_path}/preprocessor_{target}.pkl')
    
    # transform the encoded test data with preprocessor
    test_prepr = preprocessor.transform(ctb_encoder(test_id, target, id))

    # del num and reminder from col names
    test_prepr.columns = [col.split("__")[1] if "__" in col else col for col in test_prepr.columns]
    
    # add diff target columns to preprocessed data
    test_id[f'{target}_diff'] = test_id[target] - test_id[f'{target}_shift_1']
    test_id.fillna(value={f'{target}_diff':0}, inplace=True)
    test_prepr[f'{target}_diff'] = test_id[f'{target}_diff']

    # add 'shift_1_obs' column to preprocessed data
    test_prepr[f'{target}_shift_1_obs'] = test_id[f'{target}_shift_1']

    # replace null values with -100 for correct work of VectorAssembler. -100 is out of range after preprocessing by PowerTransformer
    test_prepr = test_prepr.fillna(-100)

    # add target columns to preprocessed data
    test_prepr[f'{target}'] = test_id[target]

    # add row_number_by_id column
    test_prepr['row_number_by_id'] = test_prepr.sort_values(['id_obs', 'ctrl_stamp_ns']).groupby('id_obs').cumcount()


    return test_prepr