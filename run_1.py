import json
import run_experiments 


param_dict_1 = {
    "mutation_rate": 20,
    "mutation_amount": 20,
    "range_restriction": 300,
    "initial_rule_limit": 2,
    "index_key": "Date_datetime",
    "add_subtract_percent": 50,
    "change_percent": 50,
    "max_mutation_tries": 10,
    "population_size": 150, 
    "top_rules": 10,
    "generations": 150,
    "sequence": True,
    "sequence_limit": 20,
    "tournament_size": 15,
    "dominance": False
}


npp_named_sites = ['npp_c_cali', 'npp_c_grav', 'npp_c_sand', 'npp_g_basn', 'npp_g_ibpe', 'npp_g_summ', 'npp_m_nort', 'npp_m_rabb', 'npp_m_well', 'npp_p_coll', 'npp_p_smal', 'npp_p_tobo', 'npp_t_east', 'npp_t_tayl', 'npp_t_west']
#npp_named_sites = ['npp_c_cali']

# runs = {
#     "1": "1",
#     "2": "2",
#     "3": "3"
#     }
# params_dicts = {
#     "1": param_dict_1,
#     "2": param_dict_2,
#     "3": param_dict_3,
#     "4": param_dict_4
# }

runs = {
    "1": "1",
    }
params_dicts = {
    "1": param_dict_1,
}

#NAME - {phase_name}_{parameter_index}_{Run}
phase_name = "Vital_Sequence_1
key="frost"
for param_dict_index in list(params_dicts.keys()):
    for run_index in list(runs.keys()):
        name = f'{phase_name}_{param_dict_index}_{run_index}'
        sequence_val = params_dicts[param_dict_index]["sequence"]
        run_experiments.run_experiments(phase_name, params_dicts[param_dict_index], name, npp_named_sites, key=key, sequence=sequence_val)



