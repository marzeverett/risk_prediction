import json
import run_experiments 


param_dict_1 = {
    "mutation_rate": 20,
    "mutation_amount": 20,
    "initial_rule_limit": 2,
    "range_restriction": 50,
    "index_key": "Date_datetime",
    "add_subtract_percent": 30,
    "change_percent": 70,
    #"add_subtract_percent": 50,
    #"change_percent": 50,
    "max_mutation_tries": 10,
    "population_size": 50, 
    "top_rules": 10,
    "generations": 50,
    "tournament_size": 2,
    "dominance": True,
    "sequence": True,
    "sequence_limit": 10,
    "df_list": True
}

#cases = [818, 4481]
cases = ["3719"]

runs = {
    "1": "1",
    }
params_dicts = {
    "1": param_dict_1,
}

#NAME - {phase_name}_{parameter_index}_{Run}
phase_name = "Vital_Sequence_1"
key="gluc_risk"
for param_dict_index in list(params_dicts.keys()):
    for run_index in list(runs.keys()):
        name = f'{phase_name}_{param_dict_index}_{run_index}'
        sequence_val = params_dicts[param_dict_index]["sequence"]
        run_experiments.run_experiments(phase_name, params_dicts[param_dict_index], name, cases, key=key, sequence=sequence_val, df_list=True)



