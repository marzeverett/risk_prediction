import json
import pandas as pd 
import random 
import math 
import copy 
import os 

from sklearn import metrics 

#Help from here: https://analyticsindiamag.com/evaluation-metrics-in-ml-ai-for-classification-problems-wpython-code/


#This file is for making a predictor based on a rule. 
#df = pd.read_csv("frost_csvs/npp_c_cali.csv")

def load_rules(filename):
    with open(filename) as f:
        rules_list = json.load(f)
    return rules_list
    #print(json.dumps(rules_list, indent=4))


def build_rule_prediction_query(rule):
    parameters_dict = rule["parameters"]
    query_string = ''
    first = 1
    for param in list(parameters_dict.keys()):
        lower = parameters_dict[param]["lower_bound"]
        upper = parameters_dict[param]["upper_bound"]
        if not first:
            query_string = query_string + ' & '
        query_string = query_string + f'{param} >= {lower} & {param} <= {upper}'
        first = 0
    return query_string


#Build the query for a specific parameter 
def build_specific_param_query(param_name, param):
    lower = param["lower_bound"]
    upper = param["upper_bound"]
    query_string = f'{param_name} >= {lower} & {param_name} <= {upper}'
    return query_string

#Get rule sequence bounds and earliest parameter name 
def get_rule_sequence_bounds_and_earliest(rule):
    parameters_dict = rule["parameters"]
    bounds = []
    earliest = None
    latest = None
    earliest_param_name = None 
    for param in list(parameters_dict.keys()):
        sub_latest = parameters_dict[param]["seq_lower_bound"]
        sub_earliest = parameters_dict[param]["seq_upper_bound"]
        if earliest == None:
            earliest = sub_earliest
            latest = sub_latest
            earliest_param_name = param
        else:
            if sub_earliest > earliest:
                earliest = sub_earliest
                earliest_param_name = param
            if sub_latest < latest:
                latest = sub_latest
    return earliest, latest, earliest_param_name


def count_parameter_matches(rule, sub_df, earliest):
    parameters_dict = rule["parameters"]
    return_val = True
    for param in list(parameters_dict.keys()): 
        sub_latest = parameters_dict[param]["seq_lower_bound"]
        sub_earliest = parameters_dict[param]["seq_upper_bound"]
        total_range = sub_earliest - sub_latest
        start_val = earliest - sub_earliest
        end_val = start_val + total_range
        #Get the appropriate slice and evaluate 
        df_slice = sub_df.iloc[start_val:end_val+1]
        query = build_specific_param_query(param, parameters_dict[param])
        bool_df = sub_df.eval(query)
        if bool_df.sum() < 1:
            return False
    return True

        
#Takes in a sequence rules, a dataframe (to predict on)
#Look at this for evaluations when it comes to ensemble rules as well. 
def get_sequence_predictions(rule, test_df):
    predict_df = test_df.copy()
    predict_df = predict_df.assign(predictions=0)
    #You'll have to get the outer bounds for the rule again
    earliest, latest, earliest_param_name = get_rule_sequence_bounds_and_earliest(rule)
    #Get each row 
    total_range = earliest - latest 
    #Have to think about how this is going to work when it comes to evaluations
    start_val = 0 
    end_val = start_val + total_range
    first_valid_index = end_val
    while end_val < len(test_df.index):
        #Slice the dataframe: 
        #iloc is exclusive on the end val 
        sub_df = test_df.iloc[start_val:end_val+1]
        #See if all the parameters match up 
        result = count_parameter_matches(rule, sub_df, earliest)
        if result == True:
            #Note sure this is the correct syntax 
            predict_df.loc[end_val, "predictions"] = 1
        start_val += 1
        end_val += 1
    return predict_df, first_valid_index

#Takes in a rule, a dataframe (to predict on), and returns predictions.
def get_predictions_from_rule(rule, test_df, sequence=False, df_list=False):
    if sequence:
        if df_list:
            predict_df_list = []
            valid_indexes_list = []
            for nested_df in test_df:
                predict_df, first_valid_index = get_sequence_predictions(rule, nested_df)
                predict_df.fillna(0, inplace=True)
                predict_df["predictions"] = predict_df["predictions"].astype(int)
                predict_df_list.append(predict_df)
                valid_indexes_list.append(first_valid_index)
            return predict_df_list, valid_indexes_list
        else:
            #Fill any NaN with 0
            predict_df, first_valid_index = get_sequence_predictions(rule, test_df)  
            predict_df.fillna(0, inplace=True)
            predict_df["predictions"] = predict_df["predictions"].astype(int)
    else:
        query = build_rule_prediction_query(rule)
        predict_df = test_df.assign(predictions=test_df.eval(query))
        predict_df["predictions"] = predict_df["predictions"].astype(int)
        first_valid_index = False
    return predict_df, first_valid_index


def get_pred_and_true(predict_df, key, first_valid_index=False, df_list=False):
    #Initial Df index length
    if first_valid_index:
        eval_df = predict_df.iloc[first_valid_index:]
    else:
        eval_df = predict_df
    pred = eval_df["predictions"].values.tolist()
    true = eval_df[key].values.tolist()
    return pred, true

#Evaluate the prediction model 
def evaluate_prediction_model(predict_df, key, model_index=0, first_valid_index=False, df_list=False):
    eval_dict = {}
    eval_dict["Rule Index"] = model_index
    if df_list:
        pred = []
        true = []
        for i in range(0, len(predict_df)):
            sub_pred, sub_true = get_pred_and_true(predict_df[i], key, first_valid_index=first_valid_index[i], df_list=df_list)
            pred = pred + sub_pred
            true = true + sub_true   
    else:
        pred, true = get_pred_and_true(predict_df[i], first_valid_index=first_valid_index[i], df_list=df_list)
    eval_dict["Accuracy"] = metrics.accuracy_score(true, pred)
    confusion_matrix = metrics.confusion_matrix(true, pred)
    values_array = confusion_matrix.ravel()
    eval_dict["True_Negatives"] = values_array[0]
    eval_dict["False_Positives"] = values_array[1] 
    eval_dict["False_Negatives"] = values_array[2]
    eval_dict["True_Positives"] = values_array[3]
    eval_dict["Precision"] = metrics.precision_score(true, pred, pos_label=1)
    eval_dict["Recall"] = metrics.recall_score(true, pred, pos_label=1)
    eval_dict["F1 Score"] = metrics.f1_score(true, pred, pos_label=1)

    return eval_dict



def get_sum_and_votes(prediction_list, vote_threshold):
    first_predictions =  prediction_list[0]
    for i in range(1, len(prediction_list)):
        first_predictions["predictions"] = first_predictions["predictions"] + prediction_list[i]["predictions"]   
    first_predictions.loc[first_predictions["predictions"] >= vote_threshold, "predictions"] = 1
    first_predictions.loc[first_predictions["predictions"] < vote_threshold, "predictions"] = 0
    return first_predictions


#This is a bit screwed up for average predictions 
def ensemble_learn(list_of_rules, test_df, sequence=False, df_list=False):
    #Get the predictions for each rule in the list
    num_models = len(list_of_rules)
    prediction_list = []
    valid_indexes = []

    num_predictors = len(list_of_rules)
    #Simple majority vote - more than half wins 
    vote_threshold = num_predictors/2 

    #Get all the prediction dfs for a single rule 
    for single_rule in list_of_rules:
        sub_df, first_valid_index = get_predictions_from_rule(single_rule, test_df, sequence=sequence, df_list=df_list)
        if df_list:
            valid_indexes.append(min(first_valid_index))
        else:
            valid_indexes.append(first_valid_index)
        #Weight them appropriately
        prediction_list.append(sub_df)

    if df_list:
        #Start with our first 
        first_predictions = []
        for nested_item in prediction_list:
            first_predictions.append(get_sum_and_votes(nested_item, vote_threshold))
    else:
        first_predictions =  get_sum_and_votes(prediction_list, vote_threshold)
    #Return things 
    if df_list:
        return first_predictions, valid_indexes
    else:
        return first_predictions, min(valid_indexes)


    if df_list:
            valid_indexes.append(min(first_valid_index))
    else:
        valid_indexes.append(first_valid_index)


def get_predictions_or(prediction_list):
    first_predictions = prediction_list[0]
    for i in range(1, len(prediction_list)):
        first_predictions["predictions"] = first_predictions["predictions"] | prediction_list[i]["predictions"]
    return first_predictions


def ensemble_learn_or(list_of_rules, test_df, sequence=False, df_list=False):
    #Get the predictions for each rule in the list
    num_models = len(list_of_rules)
    prediction_list = []
    #Get all the prediction dfs for a single rule 
    valid_indexes = []
    for single_rule in list_of_rules:
        sub_df, first_valid_index = get_predictions_from_rule(single_rule, test_df, sequence=sequence, df_list=df_list)
        if df_list:
            valid_indexes.append(min(first_valid_index))
        else:
            valid_indexes.append(first_valid_index)
        prediction_list.append(sub_df)

    if df_list:
        #Start with our first 
        first_predictions = []
        for nested_item in prediction_list:
            first_predictions.append(get_predictions_or(nested_item))
    else:
        first_predictions = get_predictions_or(prediction_list)
    #Return things 
    if df_list:
        return first_predictions, valid_indexes
    else:
        return first_predictions, min(valid_indexes)


def get_unique_fitness_rules(list_of_rules):
    fitness_list = [round(list_of_rules[0]["fitness"], 4)]
    unique_fitness_rules =  [list_of_rules[0]]
    for i in range(1, len(list_of_rules)):
        if round(list_of_rules[i]["fitness"], 4) not in fitness_list:
            fitness_list.append(round(list_of_rules[i]["fitness"], 4))
            unique_fitness_rules.append(list_of_rules[i])
    return unique_fitness_rules


def complete_eval_top_rules(filepath_start, key, df, sequence=False, df_list=False):
    filename = f"{filepath_start}top_rules.json"
    if not os.path.exists(filepath_start):
        os.makedirs(filepath_start)
    rules_list = load_rules(filename)
    eval_dict_list = []
    #The individual rules 
    model_index = 0
    for rule in rules_list: 
        predict_df, first_valid_index = get_predictions_from_rule(rule, df, sequence=sequence, df_list=df_list)
        eval_dict = evaluate_prediction_model(predict_df, key, model_index=model_index, first_valid_index=first_valid_index, df_list=df_list)
        eval_dict_list.append(eval_dict)
        model_index += 1
    #Get best rules with unique fitness 
    best_unique_rules = get_unique_fitness_rules(rules_list)
    #Ensemble of best rules - average 
    #if not df_list:
    predict_df, first_valid_index = ensemble_learn(rules_list, df, sequence=sequence, df_list=df_list)
    eval_dict = evaluate_prediction_model(predict_df, key, model_index="ensemble_avg", first_valid_index=first_valid_index, df_list=df_list)
    eval_dict_list.append(eval_dict)
    #Ensemble of best unique rules - average
    predict_df, first_valid_index = ensemble_learn(best_unique_rules, df, sequence=sequence, df_list=df_list)
    eval_dict = evaluate_prediction_model(predict_df, key, model_index="ensemble_uniq_avg", first_valid_index=first_valid_index, df_list=df_list)
    eval_dict_list.append(eval_dict)
    #Ensemble of best rules - Or 
    predict_df, first_valid_index = ensemble_learn_or(rules_list, df, sequence=sequence, df_list=df_list)
    eval_dict = evaluate_prediction_model(predict_df, key, model_index="ensemble_or", first_valid_index=first_valid_index, df_list=df_list)
    eval_dict_list.append(eval_dict)
    #Ensemble of best unique rules - or
    predict_df, first_valid_index = ensemble_learn_or(best_unique_rules, df, sequence=sequence, df_list=df_list)
    eval_dict = evaluate_prediction_model(predict_df, key, model_index="ensemble_uniq_or", first_valid_index=first_valid_index, df_list=df_list)
    eval_dict_list.append(eval_dict)
    #Save it
    eval_df = pd.DataFrame(eval_dict_list)
    save_name = f"{filepath_start}rule_predictor_evaluation.csv"
    eval_df.to_csv(save_name)



#print(eval_dict)
#complete_eval_top_rules("generated_files/None/", "frost")


# for k in range(0, len(prediction_list[0])):
#             first_predictions.append(prediction_list[0][k])
#         for i in range(1, len(prediction_list)):
#             #For each sub df
#             for j in range(0, len(prediction_list[i])):
#                 first_predictions[j]["predictions"] = first_predictions[j]["predictions"] | prediction_list[i][j]["predictions"]