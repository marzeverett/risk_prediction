# frost_prediction
A repo to look at site-specific frost prediction alternative to simple machine learning models 


## Plan 
Look at different weather parameters (temp/humidity, precipitation, wind speed, wind direction) and how they relate to each other using a quantitative analysis rules genetic algorithm. 

Weekend Schedule:

Go back through the literature. Figure out non-dominance rules, other stuff
Figure out what you are going to do in terms of metrics and data wrangling. Some of this data is already wrangled, so that is helpful. 








feature1[r1, r2][d1, d2] (days before) +- feature2[r1, r2][d1, d2]

Mutate
    Can add a feature
    Can subtract a feature
    Can change the value range on a feature
    Can change the time range on a feature 


Frost Events 

Frost Event - So Many Records (x amount)
Days Preceding Frost Event - restrict the range (like maybe 3-5 days??) -- probably want to index on time. Pandas might not be the fastest for this?? 

Negative offset - search the pandas dataframe? Intelligent Query -- this is going to take forever!!!
Optimize!! 


Features of Each Site

Develop site-specific rules and dataset-wide rules. 

Test set hold out. Should leave one month out? December 2022? Random? 

This would be more useful at the 5 minute-ish margin rather than the day margin, but OH WELL.

Just really have to beat an LSTM, so that's good. (Doubtful???)




Plan:
Site-specific frost prediction modeling.
General frost prediction modeling.
Site-specific frost prediction modeling, altogether.

If time, repitelos por la modificacion temporal 

