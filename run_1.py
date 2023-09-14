import json
import run_experiments 


param_dict_1 = {
    "mutation_rate": 20,
    "mutation_amount": 20,
    "initial_rule_limit": 2,
    #range restriction was 50 previously 
    "range_restriction": 300,
    "index_key": "Date_datetime",
    "add_subtract_percent": 30,
    "change_percent": 70,
    #"add_subtract_percent": 50,
    #"change_percent": 50,
    "max_mutation_tries": 10,
    "population_size": 100, 
    "top_rules": 10,
    "generations": 50,
    "tournament_size": 2,
    "dominance": True,
    "sequence": True,
    "sequence_limit": 10,
    "df_list": True
}


param_dict_2 = {
    "mutation_rate": 20,
    "mutation_amount": 20,
    "initial_rule_limit": 2,
    #range restriction was 50 previously 
    "range_restriction": 300,
    "index_key": "Date_datetime",
    "add_subtract_percent": 50,
    "change_percent": 50,
    #"add_subtract_percent": 50,
    #"change_percent": 50,
    "max_mutation_tries": 10,
    "population_size": 200, 
    "top_rules": 10,
    "generations": 100,
    "tournament_size": 2,
    "dominance": True,
    "sequence": True,
    "sequence_limit": 10,
    "df_list": True
}

#cases = [818, 4481]


#cases = ["3719"]

cases = ["3719", "1292", "2327", "5018", "6009", "1820", "4255", "1191", "1959", "553", "3631", "2738", "818", "1590", "4283", "5693", "3524", "4684", "5837", "1231", "3930", "2267", "4573", "5983", "2272", "6246", "5607", "1900", "3694", "1785", "1018", "251"]

runs = {
    "1": "1",
    "2": "2",
    }
params_dicts = {
    "1": param_dict_1,
    "2": param_dict_2
}

#NAME - {phase_name}_{parameter_index}_{Run}
phase_name = "Vital_Sequence_1"
key="gluc_risk"
for case in cases:
    for param_dict_index in list(params_dicts.keys()):
        for run_index in list(runs.keys()):
            name = f'{phase_name}_{param_dict_index}_{run_index}_{case}'
            sequence_val = params_dicts[param_dict_index]["sequence"]
            df_list_val = params_dicts[param_dict_index]["df_list"]
            run_experiments.run_experiments(phase_name, params_dicts[param_dict_index], name, [case], key=key, sequence=sequence_val, df_list=df_list_val)



