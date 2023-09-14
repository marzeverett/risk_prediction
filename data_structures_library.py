import json
import pandas as pd 
import random 
import math 
import copy 
import time 

#CHANGE 
import ga_parameter
import ga_rule
import ga_population
import ga_predictor

#https://www.statology.org/pandas-select-rows-without-nan/

default_parameter_dict = {
    "mutation_rate": 20,
    "mutation_amount": 20,
    "range_restriction": 300,
    "initial_rule_limit": 2,
    "index_key": "Date_datetime",
    "add_subtract_percent": 30,
    "change_percent": 70,
    "max_mutation_tries": 10,
    "population_size": 20, 
    "top_rules": 3,
    "generations": 3,
    "sequence": True,
    "sequence_limit": 10,
    "tournament_size": 15,
    "dominance": False
}

consequent_dict = {
    "name": "frost",
    "type": "boolean",
    "upper_bound": 1,
    "lower_bound": 1
}

key = "frost" 

list_features_dict = {
    "Air_TempC_Avg": {
        "name": "Air_TempC_Avg",
        "type": "continuous"
    },
    "Air_TempC_Max": {
        "name": "Air_TempC_Max",
        "type": "continuous"
    },
    "Air_TempC_Min": {
        "name": "Air_TempC_Min",
        "type": "continuous"
    },
    "Relative_Humidity_Avg": {
        "name": "Relative_Humidity_Avg",
        "type": "continuous"
    },
    "Relative_Humidity_Max": {
        "name": "Relative_Humidity_Max",
        "type": "continuous"
    },
    "Relative_Humidity_Min": {
        "name": "Relative_Humidity_Min",
        "type": "continuous"
    },
    "Ppt_mm_Tot": {
        "name": "Ppt_mm_Tot",
        "type": "continuous"
    },
    "WS_ms_300cm_Avg": {
        "name": "WS_ms_300cm_Avg",
        "type": "continuous"
    },
    "WS_ms_300cm_Max": {
        "name": "WS_ms_300cm_Max",
        "type": "continuous"
    },
    "WS_ms_150cm_Avg": {
        "name": "WS_ms_150cm_Avg",
        "type": "continuous"
    },
    "WS_ms_150cm_Max": {
        "name": "WS_ms_150cm_Max",
        "type": "continuous"
    },
    "WS_ms_75cm_Avg": {
        "name": "WS_ms_75cm_Avg",
        "type": "continuous"
    },
    "WS_ms_75cm_Max": {
        "name": "WS_ms_75cm_Max",
        "type": "continuous"
    },
    "WinDir_mean_Resultant": {
        "name": "WinDir_mean_Resultant",
        "type": "continuous"
    },
    "WinDir_Std_Dev": {
        "name": "WinDir_Std_Dev",
        "type": "continuous"
    }
}



def calc_parameters(feature_dict, default_parameter_dict, df, key):
        #For each 
        for item in list(feature_dict.keys()):
            feature = feature_dict[item]
            #Load in defaults that aren't already present 
            if "name" not in list(feature.keys()):
                feature["name"] = item
            if "mutation_amount" not in list(feature.keys()):
                feature["mutation_amount"] = default_parameter_dict["mutation_amount"]
            if "range_restriction" not in list(feature.keys()):
                feature["range_restriction"] = default_parameter_dict["range_restriction"]
            if "max_mutation_tries" not in list(feature.keys()):
                feature["max_mutation_tries"] = default_parameter_dict["max_mutation_tries"]
            if "sequence" not in list(feature.keys()):
                feature["sequence"] = default_parameter_dict["sequence"]
            if feature["sequence"]:
                if "sequence_limit" not in list(feature.keys()):
                    feature["sequence_limit"] = default_parameter_dict["sequence_limit"]
            #Get max and min value for feature if they were not provided
            if "lower_bound" not in list(feature.keys()):
                feature["lower_bound"] = df[feature["name"]].min()
            if "upper_bound" not in list(feature.keys()):
                feature["upper_bound"] = df[feature["name"]].max()   
            #If continuous, calculate mean and stdev 
            #NOTE: Not actually sure this would work for a nominal variable? 
            if feature["type"] == "continuous" or feature["type"] == "nominal":
                feature["mean"] = df[feature["name"]].mean() 
                feature["stdev"] = df[feature["name"]].std() 
            #Add the keys were the feature is present
            #Need to fix this part 
            df_keys = df[~df[feature["name"]].isna()]
        return feature_dict


def calc_consequent_support(consequent_dict, df):
    param_name = consequent_dict['name']
    lower_bound = consequent_dict['lower_bound']
    upper_bound = consequent_dict['upper_bound']
    query = f'{param_name} >= {lower_bound} & {param_name} <= {upper_bound}'
    sub_df = df.eval(query)
    num_consequent = sub_df.sum()
    consequent_support = num_consequent/len(df.index)
    indexes = sub_df[sub_df].index
    index_list = indexes.tolist()
    return consequent_support, num_consequent, index_list



# df = pd.read_csv("frost_csvs/npp_c_cali.csv")
# features_dict = calc_parameters(list_features_dict, default_parameter_dict, df, key)
# key = "frost"
# consequent_support, num_consequent, consequent_indexes = calc_consequent_support(consequent_dict, df)


##Params 
# param_name = "Air_TempC_Avg"
# param = ga_parameter.parameter(param_name, features_dict)
# param.print_current()
# param.mutate()
# param.print_current()
#print(json.dumps(features_dict, indent=4))


##Rules 
# the_rule = ga_rule.rule(default_parameter_dict, features_dict, consequent_dict, consequent_support, num_consequent, consequent_indexes, df)
# the_rule.elegant_print()
# the_rule.print_fitness_metrics()
# the_rule.mutate(df)
# print("After Mutation")
# the_rule.elegant_print
# the_rule.print_fitness_metrics()
# the_rule.print_self()

# #Population 
# pop = ga_population.population(default_parameter_dict, consequent_dict, list_features_dict, key, df)
# pop.run_experiment()




# print(len(test_df.index))
df = pd.read_csv("vital_csvs/3719_resampled.csv")

num_rows = len(df.index)
#0.1 - 10 percent training set - kind of a magic number 
split_index = num_rows - math.ceil(num_rows*0.2)
#print(num_rows)
#print(split_index)
train_df = df.iloc[:split_index, :]
test_df = df.iloc[split_index:, :]
test_df = test_df.reset_index()

filename = f"generated_files/Vital_Sequence_1_1_1_3719/"
key = "gluc_risk"
ga_predictor.complete_eval_top_rules(filename, key, [test_df], sequence=True, df_list=True)
