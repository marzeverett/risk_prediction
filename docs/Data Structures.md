# Data Structures

## Dataframe:
Contains ALL the data for the given task. 
Assumptions:
* Data is all-numeric. Boolean values should be 0 or 1. Categorical variables should be coded.  

## Default Parameter Dict 
Contains:
(Required: The following MUST be provided)
* mutation_rate: % of amount of individuals in a population to mutate 
* mutation_amount: % for percent amount of mutation. By default, the upper and lower bound are percentages of the standard deviation for that metric. 
* range_restriction: % of % of stdev of range to constrain value in. Only valid for continuous values.
(Optional)
* index_key: for sequences, if necessary,
* add_subtract percent: the percent chance of adding or subtracting a parameter when mutating
* change percent: the percent chance of change a parameter bounds when mutating
* max_mutation_tries: the maximum number of tries to mutate a parameter legally before giving up and not mutating
* population_size: the size of the population 
* top_rules: the number of top rules (by fitness) to keep track of
* generations: the number of generations to run the algorithm for  
* tournament_size: the size of the tournament pool when selecting the next generation
* dominance: whether to get rid of dominanted rules. If False, bottom 20% fitness rules are dropped from the population. 


    default_parameter_dict = {
        "mutation_rate": 20,
        "mutation_amount": 20,
        "range_restriction": 50,
        "index_key": "Date_datetime",
        "add_subtract_percent": 30,
        "change_percent": 70,
        "max_mutation_tries": 10,
        "population_size": 20, 
        "top_rules": 3,
        "generations": 3.
        "tournament_size": 15,
        "dominance": True
    }

## Feature-Specific Parameter Dict
Contains:  
(Required: The following MUST be provided per-feature)
* name: Name of the feature in question. Should be the same name of the column in the associated data frame. 
* type: continuous, nominal, or boolean. Continuous can take any value within a range. Nominal is a discrete number within a range. Boolean is 1 (True) or 0 (False)
(Optional: You can provide this, or it can be overrided by a global parameter or by dataframe-specific calculation, depending on the type of variable)
* upper_bound: The maximum value the parameter can take (inclusive). If not passed in, it will be calculated from the dataframe. 
* lower_bound" The minimum value the parameter can take (inclusive). If not passed in, it will be calculated from the dataframe. 
* mutation_amount: upper and lower bound for % of stdev the parameter can take. If not passed in, will default to the global parameter dict.
NOTE: You need to figure out a way to make the mutation rate be based on something else, methinks? 
* range restriction: (See global parameter dict)

(Added: These are added by calculation by the system)
* mean: Mean value of feature (if continuous)
* mode: ? No. 
* upper_bound: max value of feature
* lower_bound: min value of feature
* stdev: standard deviation of feature 
* mutation_method: (Fill in later)
* present_keys: List of key values of records in main dataframe that contain the parameter. (Might be "ALL"?)


## Consequent Dict 
Contains:
(Required)
* name of parameter consequent
* type: (same as feature)
* upper_bound: upper bound of interval of interest
* lower_bound: lower bound of interval of interest 
(Added)
included_records: List of key values of records in main dataframe that contains the feature in this range. 


## Mutation Methods
### Continous Variable
Upper and lower value are percent of standard deviation it can mutate from (positive or negative). Random percent is selected from the range (max or min), and applied to the parameter. If the amount is outside the max or min value, it clips to that value. If the value is already max or min, the mutation percent can only be in the opposite direction. 

### Nominal Variable
Assuming nominal variable is coded (discrete). Stdev is percent of change, rounded to a whole number. Same rules for clipping to max and min and direction of change apply here as to the continuous variable. 

### Boolean Variable
Upper and Lower Bound are percent of chance of flipping its value (0 or 1 or 1 to 0)

## Parameter Class: 

### Initalization: 
Takes in:
    (Required)
    Name: The name of the parameter it should be initialized to
    Feature Specific Dict (calculated parameters)
    (Optional)
    Initial Value: (Otherwise randomly chosen within interval)


        
## Whole Process 
Create an initial population of rules 
    To create a rule:
        Consequent always the same (for now)
        Antencedent Randomly Initialized
            Range of allowed values in a rule (or penalty, or something)
            1+ Parameters
                Parameter Boundaries randomly initialized
            Could chromosome with all parameters? Not sure we want to

Evaluate the fitness of the rules. Keep the N best rules in a list of some kind 

For each generation:
    Evaluate each rule based on fitness (rule-wise)
    Get rid of any "dominated" population rules (population-wise, rule-wise)
    Update the 10 best rules list (population-wise, rule-wise)
    Replace "dead" population members: (population-wise, -> rule, -> param init (potentially))
        Slim chance: By one of the 10 best rules
        Much higher chance: Random init. 
    
    Next generation of population ideas: (population-wise)
        Randomly kill select percentage, reseed?
        Tournament Selection?
        Crossover?

    Mutate percentage of the population (pop-rule-parameter)

    Repeat 

A parameter needs to be able to:
    Give its current values
    Mutate Itself (Check!)
    Probably print itself too 

A rule needs to be able to:
    Randomly init itself
        1+ parameters in antecedent 
        
    Mutate Itself:
        Randomly add or drop parameters
        Randomly change the bounds on parameters
    Print itself
    Give its fitness 

A population needs to be able to: 
    ? 


    
## Saving Scheme
For a particular Phase, Parameter, and Run
Saved in folder: {Phase_Name}_{Parameter_Index}_{Run}
    Files:
    Top Rules (List)
    All Rules (List)
    Rule Predictor Evaluation 
