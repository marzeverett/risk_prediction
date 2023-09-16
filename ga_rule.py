import json
import pandas as pd 
import random 
import math 
import copy 
import ga_parameter


#Not easy but fairly straightforward, at least. 
#First, let's worry about init'ing and eval'ing. Then,
#Lets worry about the scoring. 

#The scoring is 90% of the work here. 

#This is probably the place where most of the optimizations will need to take place
#Look at this article for queries: https://saturncloud.io/blog/the-fastest-way-to-perform-complex-search-on-pandas-dataframe/ 
#https://stackoverflow.com/questions/41125909/find-elements-in-one-list-that-are-not-in-the-other

#######################       RULE CLASS             #########################################
class rule:
    def __init__(self, default_parameter_dict, features_dict, consequent, consequent_support, num_consequent, consequent_indexes, df):
        self.features_dict = features_dict.copy()
        self.parameter_list = list(self.features_dict.keys())
        self.mutation_rate = default_parameter_dict["mutation_rate"]
        self.add_subtract_percent = default_parameter_dict['add_subtract_percent']
        self.change_percent = default_parameter_dict['change_percent']
        self.max_mutation_tries = default_parameter_dict["max_mutation_tries"]
        self.sequence = default_parameter_dict["sequence"]
        if "df_list" in list(default_parameter_dict.keys()):
            self.df_list = default_parameter_dict["df_list"]
        else:
            self.df_list = False
        if "initial_rule_limit" in list(default_parameter_dict.keys()):
            self.init_max_params = default_parameter_dict["initial_rule_limit"]
        else:
            self.init_max_params = math.ceil(0.6*len(self.parameter_list))
        self.consequent_dict = consequent
        self.consequent_support = consequent_support
        self.num_consequent = num_consequent
        self.consequent_indexes = consequent_indexes
        if self.df_list:
            self.total_records = 0
            for nested_df in df:
                self.total_records += len(nested_df.index)
        else:
            self.total_records = len(df.index)
        self.rule_dict = {}
        self.active_parameters = []
        self.last_mutation_type = None
        #CHECK: Magic Number Alert 
        self.max_init_tries = 5
        
        
        #Make sure we initialize the rule to something actually in the dataset 
        self.antecedent_support = 0
        init_initial = 0
        while self.antecedent_support <= 0.0 and init_initial <= self.max_init_tries:
            self.random_init()
            self.calc_antecedent_support(df)
            init_initial += 1
        self.calc_fitness(df)


    def random_init(self):
        self.rule_dict = {}
        self.active_parameters = []
        #One rule
        #Pick a number of parameters
        num = random.uniform(0, self.init_max_params)
        working_list = self.parameter_list.copy()
        round_num = math.ceil(num)
        if round_num == 0:
            round_num = 1
        #For the number of parameters we decided to go with 
        for i in range(0, round_num):
            #Pick a parameter
            parameter_name = random.choice(working_list)
            #Pop that off the working list
            working_list.remove(parameter_name)
            #Init the parameter
            #Add it to the rule dict, indexed by its name 
            self.rule_dict[parameter_name] = ga_parameter.parameter(parameter_name, self.features_dict)
            self.active_parameters.append(parameter_name)
            


    def build_rule_antecedent_query(self):
        query_string = ''
        first = 1
        for item in list(self.rule_dict.keys()):
            lower, upper = self.rule_dict[item].return_bounds()
            if not first:
                query_string = query_string + ' & '
            query_string = query_string + f'{item} >= {lower} & {item} <= {upper}'
            first = 0
        self.antecedent_support_query = query_string
        return query_string

    def build_consequent_query(self):
        param_name = self.consequent_dict['name']
        lower_bound = self.consequent_dict['lower_bound']
        upper_bound = self.consequent_dict['upper_bound']
        query = f'{param_name} >= {lower_bound} & {param_name} <= {upper_bound}'
        self.consequent_support_query = query
        return query 


    def build_param_specific_query(self, param_name):
        parameter = self.rule_dict[param_name]
        lower, upper = parameter.return_bounds()
        query = f'{param_name} >= {lower} & {param_name} <= {upper}'
        return query  

    #This is going to have to change for the consequent 
    def check_all_in_slice(self, param_list, df, start_offset):
        #For each other param
        for param_name in param_list:
            latest, earliest = self.rule_dict[param_name].return_seq_bounds()
            param_range = earliest - latest
            start_val = start_offset - earliest
            end_val = start_val + param_range
            #Get the slice that this param represents         
            df_slice = df.iloc[start_val:end_val+1, :]
            query = self.build_param_specific_query(param_name)
            #If ANY are within the values for this slice, good to go. 
            sub_df = df_slice.eval(query)
            if sub_df.sum() < 1:
                return False
        return True



    def count_params_fitting_indexes(self, df, total_range, index_list, param_list, earliest, consequent=False):
        num_true = 0
        for index_val in index_list:
            try:
                end_val = index_val + total_range
                if consequent:
                    df_slice = df.iloc[index_val:end_val, :] 
                else:
                    df_slice = df.iloc[index_val:end_val+1, :] 
                result = self.check_all_in_slice(param_list, df_slice, earliest)
                if result:
                    num_true += 1
            except Exception as e:
                pass 
                #print(f"Couldn't slice this {index_val} {total_range+1}: {e}")
        return num_true


    #Get the support of the antecedent for a sequence. 
    def calc_antecedent_support_sequence(self, df):
        earliest, latest, earliest_param_name = self.get_rule_sequence_bounds_and_earliest_param()
        total_range = earliest - latest 
        if self.df_list:
            total_applicable = 0
            for nested_df in df:
                if earliest - latest > 0:
                    total_applicable += math.floor(len(nested_df.index)-(earliest-latest))
                else:
                    total_applicable += len(nested_df.index)
        else:
            if earliest - latest > 0:
                total_applicable = math.floor(len(df.index)-(earliest-latest))
            else:
                total_applicable = len(df.index)
        #If there is only one parameter in the rule, or if somehow only one slice of the sequence is present 
        if total_range == 0 or len(self.active_parameters) < 2:
            #Then its just going to be the normal non-sequence support calc
            self.calc_antecedent_support_non_sequence(df)
            if total_applicable > 0:
                self.antecedent_support = self.num_antecedent/total_applicable
        else:
            #Find everywhere in the dataframe (each time sequence index) where it occurs
            query = self.build_param_specific_query(earliest_param_name)
            #print(query)
            if self.df_list:
                index_list = []
                for nested_df in df:
                    bool_df = nested_df.eval(query)
                    indexes = bool_df[bool_df].index
                    index_list.append(indexes.tolist())
            else:
                bool_df = df.eval(query)
                indexes = bool_df[bool_df].index
                index_list = indexes.tolist()
            remaining_params = self.active_parameters.copy()
            remaining_params.remove(earliest_param_name)
            num_true = 0
            if self.df_list:
                for i in range(0, len(df)):
                    #Get the count
                    num_true += self.count_params_fitting_indexes(df[i], total_range, index_list[i], remaining_params, earliest)
            else:
                num_true = self.count_params_fitting_indexes(df, total_range, index_list, remaining_params, earliest)
            self.num_antecedent = num_true
            if total_applicable > 0:
                self.antecedent_support = self.num_antecedent/total_applicable
            else:
                self.antecedent_support = 0





    def calc_antecedent_support_non_sequence(self, df):
        #Takes in itself and the dataframe, and calculates its support 
        antecedent_support_query = self.build_rule_antecedent_query()
        if self.df_list:
            sub_total = 0
            total_applicable = 0
            for nested_df in df:
                sub_df = nested_df.eval(antecedent_support_query)
                sub_total += sub_df.sum()
                total_applicable += len(nested_df.index)
            self.num_antecedent = sub_total
        else:
            sub_df = df.eval(antecedent_support_query)
            self.num_antecedent = sub_df.sum()
            total_applicable = self.total_records
        self.antecedent_support = self.num_antecedent/total_applicable


    def calc_antecedent_support(self, df):
        if self.sequence:
            self.calc_antecedent_support_sequence(df)
        else:
            self.calc_antecedent_support_non_sequence(df)

    
    def calc_overall_support_sequence(self, df):
        earliest, latest, earliest_param_name = self.get_rule_sequence_bounds_and_earliest_param()

        if self.df_list:
            total_applicable = 0
            for nested_df in df:
                if earliest - latest > 0:
                    total_applicable += math.floor(len(nested_df.index)-(earliest-latest))
                else:
                    total_applicable += len(nested_df.index)
        else:
            if earliest - latest > 0:
                total_applicable = math.floor(len(df.index)-(earliest-latest))
            else:
                total_applicable = len(df.index)
        #Might want to make this something that is always calculated 
        total_range = earliest - latest 
        remaining_params = self.active_parameters.copy()
        if self.df_list:
            num_true = 0
            for i in range(0, len(df)):
                num_true += self.count_params_fitting_indexes(df[i], total_range, self.consequent_indexes[i], remaining_params, earliest, consequent=True)
        else:
            num_true  = self.count_params_fitting_indexes(df, total_range, self.consequent_indexes, remaining_params, earliest, consequent=True)
        self.num_whole_rule = num_true
        if total_applicable > 0:
            self.support = self.num_whole_rule/total_applicable
        else:
            self.support = 0


    def calc_overall_support_non_sequence(self, df):
        #Assumes you have already built the antecedent and consequent support queries
        overall_support_query =f"{self.antecedent_support_query} & {self.consequent_support_query}"
        sub_df = df.eval(overall_support_query)
        self.num_whole_rule = sub_df.sum()
        self.support = self.num_whole_rule/self.total_records


    def calc_overall_support(self, df):
        if self.sequence:
            self.calc_overall_support_sequence(df)
        else:
            self.calc_overall_support_non_sequence(df)

    def calc_confidence(self):
        if self.num_antecedent != 0:
            self.confidence = self.num_whole_rule/self.num_antecedent
        else:
            self.confidence = 0.0

    def calc_lift(self):
        self.lift = self.confidence/self.consequent_support

    def calc_fitness(self, df):
        #Build the queries 
        self.build_rule_antecedent_query()
        self.build_consequent_query()
        #Get the metrics you need for calculations
        self.calc_antecedent_support(df)
        self.calc_overall_support(df)
        self.calc_antecedent_support(df)
        #We don't need the dataframe for the last one since we have already calculated what we need 
        self.calc_confidence()
        self.calc_lift()
        #This is a dummy for now! 

        #self.fitness = self.support * self.confidence * self.lift
        #Also kind of a dummy. Need to re-look at dominance 
        self.fitness = (2*self.support * (self.num_whole_rule/self.num_consequent))*self.confidence*self.lift

    #Gets the earliest sequence value (higher number), latest sequence value (lower number), and param with earliest sequence number 
    def get_rule_sequence_bounds_and_earliest_param(self):
        if self.sequence:
            latest = None
            earliest = None 
            earliest_param_name = None
            for item in list(self.rule_dict.keys()):
                sub_latest, sub_earliest = self.rule_dict[item].return_seq_bounds()
                if latest == None:
                    latest = sub_latest
                    earliest = sub_earliest
                    earliest_param_name = item
                else:
                    if sub_earliest > earliest:
                        earliest = sub_earliest
                        earliest_param_name = item
                    if sub_latest < latest:
                        latest = sub_latest
            return earliest, latest, earliest_param_name
        else:
            return False, False, False
    
    def get_fitness(self):
        return self.fitness
    
    def get_rule_dict(self):
        return self.rule_dict.copy()

    def get_rule_dict_all_numeric(self):
        new_rule_dict = {}
        new_rule_dict["parameters"] = {}
        for param in list(self.rule_dict.keys()):
            #Solve this? 
            new_rule_dict["parameters"][param] = {}
            new_rule_dict["parameters"][param]["lower_bound"] = self.rule_dict[param].curr_lower_bound
            new_rule_dict["parameters"][param]["upper_bound"] = self.rule_dict[param].curr_upper_bound
            if self.sequence:
                new_rule_dict["parameters"][param]["seq_lower_bound"] = self.rule_dict[param].curr_sequence_lower
                new_rule_dict["parameters"][param]["seq_upper_bound"] = self.rule_dict[param].curr_sequence_upper
        new_rule_dict["support"] = self.support
        new_rule_dict["confidence"] = self.confidence
        new_rule_dict["lift"] = self.lift
        new_rule_dict["fitness"] = self.fitness
        return new_rule_dict

    def get_bounds_list(self):
        bounds_list = []
        rule_keys = list(self.rule_dict.copy())
        rule_keys = sorted(rule_keys)
        for key in rule_keys:
            bounds_list.append(self.rule_dict[key].curr_lower_bound)
            bounds_list.append(self.rule_dict[key].curr_upper_bound)
        return bounds_list
    def get_active_parameters(self):
        return self.active_parameters

    def add_parameter(self):
        #Get the parameters we aren't currently using
        non_included_params = list(set(self.parameter_list) - set(self.active_parameters))
        #Pick a random one
        try:
            new_param = random.choice(non_included_params)
            #Init and add it 
            self.rule_dict[new_param] = ga_parameter.parameter(new_param, self.features_dict)
            self.active_parameters.append(new_param)
        except Exception as e:
            pass 
            #This probably means we already have all parameters - so skip 
            #Mutation for now. 


    def subtract_parameter(self):
        #Pick a param in the rule 
        delete_param = random.choice(self.active_parameters)
        self.active_parameters.remove(delete_param)
        self.rule_dict.pop(delete_param)


    def perform_mutation(self, df, kind=None):
        add_chance = self.add_subtract_percent/2
        subtract_chance = add_chance
        change_chance = self.change_percent 
        if kind == None:
            kind_of_mutation = random.choices(["add", "subtract", "change"], weights=[add_chance, subtract_chance, change_chance], k=1)[0]
        else:
            kind_of_mutation = kind
        #START HERE! 
        #Add or subtract 
        if kind_of_mutation == "add":
            self.add_parameter()
            self.last_mutation_type = "add"
        elif kind_of_mutation == "subtract":
            #Only subtract if there is more than one parameter. Otherwise add
            if len(self.active_parameters) < 2:
                self.last_mutation_type = "add"
                self.add_parameter()
            #Otherwise, random choice of add or subtract 
            else:
                self.last_mutation_type = "subtract"
                self.subtract_parameter()
        #Or, change the boundaries 
        else:
            self.last_mutation_type = "change"
            mutate_param = random.choice(self.active_parameters)
            self.rule_dict[mutate_param].mutate()
        return kind_of_mutation
        
    #Get rid of print statements here eventually! 
    def mutate(self, df, kind=None): 
        #Use the percentages to figure out what kinds of mutation to do 
        old_rule_dict = self.rule_dict.copy()
        old_active_params = self.active_parameters.copy()
        kind_of_mutation = self.perform_mutation(df)
        self.calc_fitness(df)
        tries = 0 
        #If we mutated into something not present, try again. 
        if self.antecedent_support <= 0.0 and tries < self.max_mutation_tries:
            tries += 1
            self.rule_dict = old_rule_dict
            self.active_parameters = old_active_params
            self.perform_mutation(df, kind=kind_of_mutation)
            self.calc_fitness(df)

                    
    def print_full(self):
        print(f"Mutation Rate {self.mutation_rate}")
        print(f"Maximum allowed initial parameters {self.init_max_params}")
        print(f"Last Mutation {self.last_mutation_type}")
        print(f"Active parameters {self.active_parameters}")
        for rule in self.active_parameters:
            self.rule_dict[rule].print_name()
            self.rule_dict[rule].print_current()
        self.print_fitness_metrics()

    def print_self(self):
        print(f"Last Mutation {self.last_mutation_type}")
        print(f"Active parameters {self.active_parameters}")
        for rule in self.active_parameters:
            self.rule_dict[rule].print_name()
            self.rule_dict[rule].print_current()

    def print_fitness_metrics(self):
        print(f"Antecedent Support {self.antecedent_support}")
        print(f"Consequent Support {self.consequent_support}")
        print(f"Overall Support {self.support}")
        print(f"Confidence {self.confidence}")
        print(f"Lift {self.lift}")
        print(f"Overall Fitness {self.fitness}")

    def elegant_print(self):
        if self.sequence:
            for item in list(self.rule_dict.keys()):
                print(f"{item}: [{round(self.rule_dict[item].curr_lower_bound, 3)}, {round(self.rule_dict[item].curr_upper_bound, 3)}]  [{self.rule_dict[item].curr_sequence_lower}, {self.rule_dict[item].curr_sequence_upper}]")
        else:
            for item in list(self.rule_dict.keys()):
                print(f"{item}: [{round(self.rule_dict[item].curr_lower_bound, 3)}, {round(self.rule_dict[item].curr_upper_bound, 3)}]")
     

    #I think we need this in order to be able to sort...
    def __lt__(self, other):
         return self.fitness < other.fitness
