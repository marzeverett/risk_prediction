import pandas as pd
import json 
import os



#FOLDER
#{phase_name}/{phase_name}_{param_index}_{run}_{site}
#rule_predictor_evaluation.csv
#top_rules.json
#all_rules.json

#Rule Index, Accuracy, True_Negatives, False_Positives, False_Negatives, True_Positives, Precision, Recall, F1 Score
#Rules indexes 0-14
#Ensemble Indexes: ensemble_avg, ensemble_or, ensemble_uniq_avg, ensemble_uniq_or 

#rules_indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
rules_indexes = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
ensemble_indexes = ["ensemble_avg", "ensemble_or", "ensemble_uniq_avg", "ensemble_uniq_or"]

def return_best_dict():
    best_dict = {
    "rule_wise": {
        "best_index": [],
        "param_index": [],
        "run": [],
        "f1": [],
        "accuracy": [],
        "false_negatives": [],
    },
    "ensemble_wise": {
        "best_index": [],
        "param_index": [],
        "run": [],
        "f1": [],
        "accuracy": [],
        "false_negatives": [],
    }

    }
    return best_dict.copy()


def return_aggregate_dict():
    aggregate_dict = {
        "site": [],
        "metric": [],
        "param_index": [],
        "run_index": [],
        "indexes": [],
        "accuracies": [],
        "false_negatives": []
    }
    return aggregate_dict.copy()

check_slices = ["rule_wise", "ensemble_wise"]
def best_per_site(file_start, phase, params, runs, sites):
    #Here we'll want to separate single rules from ensembles. 
    #For every site:
    for slice_wise in check_slices:
        if slice_wise == "rule_wise":
            check_index = rules_indexes
        else:
            check_index = ensemble_indexes
        agg_dict = return_aggregate_dict()
        for site in sites:
            best_dict = return_best_dict()
            #For each parameter index
            max_f1_rules = None
            max_row_rules = None
            best_param = None
            best_run = None
            for param in params:
                ##For each run, load in the performance csv
                for run in runs:
                    df = pd.read_csv(f"{file_start}{phase}/{phase}_{param}_{run}_{site}/rule_predictor_evaluation.csv")
                    #Get the best rules models 
                    rules_df = df[df["Rule Index"].isin(check_index)]

                    rules_df = rules_df[rules_df["F1 Score"] == rules_df["F1 Score"] .max()]
                    rules_max = rules_df["F1 Score"].max()
                    if max_f1_rules == None:
                        max_f1_rules = rules_max
                        max_row_rules = rules_df
                        best_param = param
                        best_run = run 
                    else:
                        if rules_max > max_f1_rules:
                            max_f1_rules = rules_max
                            max_row_rules = rules_df
                            best_param = param
                            best_run = run 
            best_dict[slice_wise]["best_index"].append(max_row_rules["Rule Index"].tolist())
            best_dict[slice_wise]["param_index"].append(best_param)
            best_dict[slice_wise]["run"].append(best_run)
            best_dict[slice_wise]["f1"].append(max_f1_rules)
            best_dict[slice_wise]["accuracy"].append(max_row_rules["Accuracy"].tolist())
            best_dict[slice_wise]["false_negatives"].append(max_row_rules["False_Negatives"].tolist())
            
            save_start = f"{phase}_analysis/site_wise/"
            if not os.path.exists(save_start):
                os.makedirs(save_start)
            
            save_name = f'{save_start}{slice_wise}_{site}_best.csv'
            save_df = pd.DataFrame(best_dict[slice_wise])
            save_df.to_csv(save_name)           

            agg_dict["site"].append(site)
            agg_dict["metric"].append(max_f1_rules)
            agg_dict["param_index"].append(best_param)
            agg_dict["run_index"].append(best_run)
            agg_dict["indexes"].append(max_row_rules["Rule Index"].tolist())
            agg_dict["accuracies"].append(max_row_rules["Accuracy"].tolist())
            agg_dict["false_negatives"].append(max_row_rules["False_Negatives"].tolist())
        
        save_agg_name = f'{phase}_analysis/{slice_wise}_aggregate_best.csv'
        save_agg_df = pd.DataFrame(agg_dict)
        save_agg_df.to_csv(save_agg_name)
        #print(json.dumps(agg_dict, indent=4))
        
file_start = "generated_files/"
phase_name = "Initial_1"
param_indexes = [1, 2, 3, 4]
run_indexes = [1, 2, 3]
sites = ['npp_c_cali', 'npp_c_grav', 'npp_c_sand', 'npp_g_basn', 'npp_g_ibpe', 'npp_g_summ', 'npp_m_nort', 'npp_m_rabb', 'npp_m_well', 'npp_p_coll', 'npp_p_smal', 'npp_p_tobo', 'npp_t_east', 'npp_t_tayl', 'npp_t_west']

best_per_site(file_start, phase_name, param_indexes, run_indexes, sites)
 



