import json

import run_experiments 


default_parameter_dict = {
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
    "population_size": 10, 
    "top_rules": 3,
    "generations": 6,
    "tournament_size": 2,
    "dominance": True,
    "sequence": True,
    "sequence_limit": 10,
    "df_list": True
}



phase = "Testing"
name = "Test_1"
#npp_named_sites = ['npp_c_cali', 'npp_c_grav']
#npp_named_sites = ['npp_c_cali', 'npp_c_grav']
#cases = [818, 4481]
cases = ["3719"]

key="gluc_risk"
run_experiments.run_experiments(phase, default_parameter_dict, name, cases, key=key, sequence=True, all_data=False, df_list=True)



