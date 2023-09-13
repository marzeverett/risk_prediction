import json
import pandas as pd 
import random 
import math 
import copy 
#from copy import deepcopy
import ga_rule
import os 
#d = deepcopy
#https://stackoverflow.com/questions/5326112/how-to-round-each-item-in-a-list-of-floats-to-2-decimal-places 


################################################# POPULATION CLASS ###################################################################
#How many top rules to hold? 
#10% hyperparameter of number of rules to hold in top 
#See first if we can init these rules, then worry about scoring them and making new populations 
class population:
    def __init__(self, default_parameter_dict, consequent_dict, feature_dict, key, df):
        #Passes parameters
        #Magic number for now 
        self.round_num = 2

        self.df = df 
        self.default_parameter_dict = default_parameter_dict.copy()
        self.consequent_dict = consequent_dict.copy()
        self.key = key 
        if "df_list" in list(self.default_parameter_dict.keys()):
            self.df_list = self.default_parameter_dict["df_list"]
        else:
            self.df_list = False
        #Should eventually workshop
        # for item in list(feature_dict.keys()):
        #     if item not in list(self.df.columns):
        #         feature_dict.pop(item) 
        self.features_dict = self.calc_parameters(feature_dict, self.default_parameter_dict, self.df, self.key)
         
        self.consequent_support, self.num_consequent, self.consequent_indexes = self.calc_consequent_support(self.consequent_dict, self.df)
        self.mutation_rate = self.default_parameter_dict['mutation_rate']
        self.population_size = self.default_parameter_dict["population_size"]
        self.num_top_rules = self.default_parameter_dict["top_rules"]
        self.generations = self.default_parameter_dict["generations"]
        self.tournament_size = self.default_parameter_dict["tournament_size"]
        self.dominance = self.default_parameter_dict["dominance"]
        
        self.mutation_number = math.ceil(self.population_size*(self.mutation_rate/100))
        
        #List of rules 
        self.rules_pop = self.init_rules_pop()
        self.top_rules = []

        #Dominance Dict 
        self.dominance_dict = {}
        self.dominance_fitness_dict = {}
        
    
    def init_rules_pop(self):
        rules_pop = []
        for i in range(0, self.population_size):
            new_rule = ga_rule.rule(self.default_parameter_dict, self.features_dict, self.consequent_dict, self.consequent_support, self.num_consequent, self.consequent_indexes, self.df)
            #new_rule.random_init()
            rules_pop.append(new_rule)
        return rules_pop

    def calc_consequent_support(self, consequent_dict, df):
        param_name = consequent_dict['name']
        lower_bound = consequent_dict['lower_bound']
        upper_bound = consequent_dict['upper_bound']
        query = f'{param_name} >= {lower_bound} & {param_name} <= {upper_bound}'
        if self.df_list:
            index_list = []
            num_consequent = 0
            total_applicable = 0
            for nested_df in df:
                sub_df = nested_df.eval(query)
                num_consequent += sub_df.sum()
                total_applicable = len(nested_df.index)
                indexes = sub_df[sub_df].index
                #List of indexes lists 
                index_list.append(indexes.tolist())
        else:
            sub_df = df.eval(query)
            num_consequent = sub_df.sum()
            total_applicable = len(df.index)
            indexes = sub_df[sub_df].index
            index_list = indexes.tolist()
        consequent_support = num_consequent/total_applicable
        return consequent_support, num_consequent, index_list


    def calc_parameters(self, feature_dict, default_parameter_dict, df, key):
        #If its a df list, make sure to merge before calculated feature-level stuff. 
        if self.df_list:
            new_df = pd.DataFrame()
            for nested_df in df:
                if new_df.empty:
                    new_df = nested_df
                else:
                    new_df = pd.concat([new_df, nested_df], axis=0)
            df = new_df

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
            #Need to do this here, too! 
            #Get max and min value for feature if they were not provided
            if "lower_bound" not in list(feature.keys()):
                feature["lower_bound"] = df[feature["name"]].min()
            if "upper_bound" not in list(feature.keys()):
                feature["upper_bound"] = df[feature["name"]].max()   
            #If continuous, calculate mean and stdev 
            #NOTE: Not actually sure this would work for a nominal variable? 
            #Think this is the last thing? 
            if feature["type"] == "continuous" or feature["type"] == "nominal":
                feature["mean"] = df[feature["name"]].mean() 
                feature["stdev"] = df[feature["name"]].std() 
            #Add the keys were the feature is present
            #Need to fix this part 
            #df_keys = df[~df[feature["name"]].isna()]
        return feature_dict

    

    def update_top_rules(self):
        #get the top rules in the generation
        self.rules_pop.sort(reverse=True)
        #Get the top keep rules from this population:
        self.pop_top_rules = copy.deepcopy(self.rules_pop[:self.num_top_rules])
        new_pop_top_rules = []
        if self.top_rules == []:
            self.top_rules = copy.deepcopy(self.pop_top_rules)
        #SO UGLY - CHECK 
        else:
            for rule in self.pop_top_rules:
                #Assume not same
                same = False
                for other_rule in self.top_rules:
                    active_params = rule.get_active_parameters()
                    other_active_params = other_rule.get_active_parameters()
                    bounds = rule.get_bounds_list()
                    bounds = [round(item, self.round_num) for item in bounds]
                    other_bounds = other_rule.get_bounds_list()
                    other_bounds = [round(item, self.round_num) for item in other_bounds]
                    if active_params == other_active_params and bounds == other_bounds:
                        same = True
                    #CHANGE here - not sure if good or not. 
                    elif active_params == other_active_params and rule.get_fitness() < other_rule.get_fitness():
                        same = True
                if same == False:
                    new_pop_top_rules.append(rule)
                    
            temp_top_list = self.top_rules + new_pop_top_rules
            temp_top_list.sort(reverse=True)
            self.top_rules = copy.deepcopy(temp_top_list[:self.num_top_rules])
            #print(len(self.top_rules))

    def mutate_population(self):
        mutate_rules = random.sample(self.rules_pop, self.mutation_number)        
        for rule in mutate_rules:
            #print(rule.print_self())
            rule.mutate(self.df)

    def update_dominance_dict(self):
        #Dominance rules need to have lower fitness to be killed, I think 
        for rule in self.rules_pop:
            rule_dict = rule.get_rule_dict()
            #Make its parameters a string - sort alpha so always same
            rule_string = str(sorted(list(rule_dict.keys())))
            #If we don't have an entry for this, make one
            if rule_string not in list(self.dominance_dict.keys()):
                self.dominance_dict[rule_string] = copy.deepcopy(rule_dict)
                self.dominance_fitness_dict[rule_string] = rule.get_fitness()
            #Otherwise:
            else:
                compare_rule_dict = self.dominance_dict[rule_string]
                dominated = True
                for param in list(rule_dict.keys()):
                    #But if it is NOT dominated on anything:
                    if round(rule_dict[param].upper_bound, self.round_num) > round(compare_rule_dict[param].upper_bound, self.round_num) and round(rule_dict[param].lower_bound, self.round_num) < round(compare_rule_dict[param].lower_bound, self.round_num):
                        dominated = False
                if dominated == False:
                    self.dominance_dict[rule_string] = copy.deepcopy(rule_dict)
                    self.dominance_fitness_dict[rule_string] = rule.get_fitness()


    def kill_dominated(self):
        new_rules_pop_list = []
        for rule in self.rules_pop:
            rule_dict = rule.get_rule_dict()
            #Make its parameters a string - sort alpha so always same
            rule_string = str(sorted(list(rule_dict.keys())))
            #print(rule_string)
            compare_rule_dict = self.dominance_dict[rule_string]
            #Assume dominated
            dominated = True
            for param in list(rule_dict.keys()):
                #But if it is NOT dominated on anything:
                #CHANGE HERE - potentially a VERY bad one. 
                if rule_dict[param].curr_upper_bound > compare_rule_dict[param].curr_upper_bound and rule_dict[param].curr_lower_bound < compare_rule_dict[param].curr_lower_bound:
                    dominated = False
            if dominated == False:
                self.dominance_dict[rule_string] = copy.deepcopy(rule_dict)
            #Add it if it's fitness is higher!
            if dominated:
                #Only keep if it has a higher fitness
                #Another potentially bad change! 
                if rule.fitness > self.dominance_fitness_dict[rule_string]:
                    new_rules_pop_list.append(rule)
                else:
                    #print("Killing ")
                    #rule.elegant_print()
                    pass 
            else:
                new_rules_pop_list.append(rule)
        self.rules_pop = new_rules_pop_list

    def tournament_competition(self): 
        #Randomly pick 4 of the rules from the rule pool
        competitors = random.sample(self.rules_pop, self.tournament_size)
        fittest = competitors[0]
        fittest_fitness = competitors[0].get_fitness()
        for i in range(1, self.tournament_size):
            curr_fitness = competitors[i].get_fitness()
            if curr_fitness > fittest_fitness:
                fittest_fitness = curr_fitness
                fittest = competitors[i]
        return copy.deepcopy(fittest)

    def tournament_selection(self):
        new_pop = []
        for i in range(0, self.population_size):
            offspring = self.tournament_competition()
            new_pop.append(offspring)
        self.rules_pop = new_pop 


    #NOTE: YOU MIGHT WANT TO DELETE 0 FITNESS INDIVIDUALS
    def run_generation(self):
        #Update dominance dict and Kill dominated rules
        #Take another look at this - might incorporate into fitness 
        if self.dominance:
            self.update_dominance_dict()
            self.kill_dominated()
        #Kill lowest 20% of rules - MAGIC NUMBER ALERT 
        else:  
            self.rules_pop.sort()
            self.rules_pop = self.rules_pop[math.ceil(len(self.rules_pop)*.20):]

        #Update the top rules
        self.update_top_rules()

        #Replace dead population members
        num_replacements = self.population_size - len(self.rules_pop)
        for i in range(0, num_replacements):
            #How will we make the next seed?
            #Magic NUMBER ALERT - CHECK 
            seed = kind_of_mutation = random.choices(["best", "new"], weights=[10, 90], k=1)[0]
            if seed == "best" and len(self.top_rules) > 0:
                new_rule = copy.deepcopy(random.choice(self.top_rules))
            else:
                new_rule = new_rule = ga_rule.rule(self.default_parameter_dict, self.features_dict, self.consequent_dict, self.consequent_support, self.num_consequent, self.consequent_indexes, self.df)
            self.rules_pop.append(new_rule)
        #Create the next generation
        self.tournament_selection()
        #Mutate percentage of population
        self.mutate_population() 


    def save_top_rules(self, name=None):
        list_of_rules = []
        for rule in self.top_rules:
            list_of_rules.append(rule.get_rule_dict_all_numeric())
        rule_save = json.dumps(list_of_rules, indent=4)
        start_string = f"generated_files/{name}/"
        if not os.path.exists(start_string):
            os.makedirs(start_string)
        save_string = f"{start_string}top_rules.json"
        with open(save_string, "w") as f:
            f.write(rule_save) 


    def save_all_rules(self, name=None):
        list_of_rules = []
        for rule in self.rules_pop:
            list_of_rules.append(rule.get_rule_dict_all_numeric())
        rule_save = json.dumps(list_of_rules, indent=4)
        start_string = f"generated_files/{name}/"
        if not os.path.exists(start_string):
            os.makedirs(start_string)
        save_string = f"{start_string}all_rules.json"
        with open(save_string, "w") as f:
            f.write(rule_save) 


    def run_experiment(self, status=False, name=None):
        #Run the generations 
        for i in range(0, self.generations):
            if status:
                print(f" Generation {i}")
            self.run_generation()
        #Save the rules 
        self.save_top_rules(name=name)
        self.save_all_rules(name=name)

    def print_self(self):
        print(f"Pop size: ", self.population_size)
        print(f"Number of top rules to retain: ", self.num_top_rules)
        
    def print_rules(self):
        print("Rules: ")
        for item in self.rules_pop:
            item.print_self()

    def print_rules_and_fitness(self):
        print("Rules: ")
        for item in self.rules_pop:
            item.print_self()
            item.print_fitness_metrics()
            print()

    
    def print_top_rules_and_fitness(self):
        print("Global top rules metrics")
        for rule in self.top_rules:
            rule.elegant_print()
            rule.print_fitness_metrics()
            print()

    def print_dominance_dict(self):
        for item in list(self.dominance_dict.keys()):
            print(self.dominance_dict[item].keys())

