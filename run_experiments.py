import pandas as pd 
import math 
import ga_population
import ga_predictor 

#Help from hee: https://www.geeksforgeeks.org/python-intersection-two-lists/

cases = {
    4481: {"index": 0},
    3719: {"index": 1},
    1292: {"index": 2},
    2327:{"index": 3},
    5018: {"index": 4},
    6009: {"index": 5},
    1820: {"index": 6},
    2332: {"index": 7},
    4255: {"index": 8},
    1191: {"index": 9},
    1959: {"index": 10},
    553: {"index": 11},
    3631: {"index": 12},
    2738: {"index": 13},
    818: {"index": 14},
    1590: {"index": 15},
    55: {"index": 16},
    4283: {"index": 17},
    5693: {"index": 18},
    5442: {"index": 19},
    3524: {"index": 20},
    4684: {"index": 21},
    5837: {"index": 22},
    1231: {"index": 23},
    6227: {"index": 24},
    985: {"index": 25},
    3930: {"index": 26},
    2267: {"index": 27},
    4573: {"index": 28},
    5983: {"index": 29},
    2272: {"index": 30},
    6246: {"index": 31},
    5607: {"index": 32},
    1900: {"index": 33},
    3694: {"index": 34},
    1785: {"index": 35},
    1018: {"index": 36},
    251: {"index": 37}
}


datastreams = {
    "orch": {
        "index": 1,
        "fields": ["Orchestra_RFTN20_CE", "Orchestra_RFTN20_CP", "Orchestra_RFTN20_CT", "Orchestra_RFTN20_RATE", "Orchestra_RFTN20_VOL"]
        },
    "snu": {
        "index": 2,
        "fields": ["SNUADC_ECG_II", "SNUADC_ECG_V5", "SNUADC_ART", "SNUADC_FEM", "SNUADC_CVP" ]
        },
    "solar": {
        "index": 3,
        "fields": ["Solar8000_VENT_MAWP", "Solar8000_VENT_RR", "Solar8000_VENT_TV", "Solar8000_VENT_PPLAT", "Solar8000_VENT_PIP", "Solar8000_VENT_MV", "Solar8000_VENT_INSP_TM", "Solar8000_BT"]
        },
}

datastream_fields = ["Orchestra_RFTN20_CE", "Orchestra_RFTN20_CP", "Orchestra_RFTN20_CT", "Orchestra_RFTN20_RATE", "Orchestra_RFTN20_VOL",
"SNUADC_ECG_II", "SNUADC_ECG_V5", "SNUADC_ART", "SNUADC_FEM", "SNUADC_CVP",
"Solar8000_VENT_MAWP", "Solar8000_VENT_RR", "Solar8000_VENT_TV", "Solar8000_VENT_PPLAT", "Solar8000_VENT_PIP", "Solar8000_VENT_MV", "Solar8000_VENT_INSP_TM", "Solar8000_BT"]

clinical_fields =  ["anestart", "aneend", "age", "sex", "height", "weight",
                     "bmi", "dx", "dis", "preop_pft", "preop_plt", "preop_pt", 
                     "preop_aptt", "preop_na", "preop_k", "preop_gluc", "preop_cr", 
                     "intraop_uo", "intraop_ffp"]

predictions = ["emop", "dis_mortality_risk", "gluc_risk"]

def return_default_parameter_dict():
    parameter_dict = {
        "mutation_rate": 20,
        "mutation_amount": 20,
        "range_restriction": 50,
        "index_key": "Date_datetime",
        "add_subtract_percent": 30,
        "change_percent": 70,
        "max_mutation_tries": 10,
        "population_size": 20, 
        "top_rules": 3,
        "generations": 3,
        "tournament_size": 15,
        "dominance": False,
        "df_list": True
    }
    return parameter_dict.copy()


def return_default_consequent_dict():
    consequent_dict = {
        "name": "gluc_risk",
        "type": "boolean",
        "upper_bound": 1,
        "lower_bound": 1
    }
    return consequent_dict.copy()

def return_default_key():
    key = "gluc_risk" 
    return key 


#Workshop later. 
def create_feature_dict(list_of_features, key, index_key):
    return_dict = {}
    for feature in list_of_features:
        if feature != key and feature != index_key: 
            sub_dict = {
                "name": feature,
                "type": "continuous"
            }
            return_dict[feature] = sub_dict
    return return_dict


def create_df_list(cases):
    df_list = []
    for case in cases:
        #Read it in 
        df = pd.read_csv(f"vital_csvs/{case}_resampled.csv")
        df_list.append(df)
    return df_list

def split_training_test(df):
    num_rows = len(df.index)
    #0.2 - 20 percent training set - kind of a magic number 
    split_index = num_rows - math.ceil(num_rows*0.2)
    train_df = df.iloc[:split_index, :]
    test_df = df.iloc[split_index:, :]
    test_df = test_df.reset_index()
    return train_df, test_df
    


def run_experiments(phase_name, default_parameter_dict, name, sites, key=None, all_data=False, sequence=False, df_list=False):
    default_dict = return_default_parameter_dict()
    default_dict.update(default_parameter_dict)
    if key == None:
        key = return_default_key()
    consequent_dict = return_default_consequent_dict()
    full_name = name
    list_features_dict = create_feature_dict(datastream_fields, key, "Time")
    df = create_df_list(sites)

    #Since we are doing this, fine for now. 
    if df_list:
        train_df = []
        test_df = []
        for nested_df in df:
            sub_train_df, sub_test_df = split_training_test(nested_df)
            train_df.append(sub_train_df)
            test_df.append(sub_test_df)
    else:
        train_df, test_df = split_training_test(df)

    #Run the experiment
    pop = ga_population.population(default_dict, consequent_dict, list_features_dict, key, train_df)
    pop.run_experiment(name=full_name)
    #Going to have to change that 
    #Eval - For each top rule and for the ensemble classifiers
    filename = f"generated_files/{full_name}/"
    ga_predictor.complete_eval_top_rules(filename, key, test_df, sequence=sequence, df_list=df_list)




