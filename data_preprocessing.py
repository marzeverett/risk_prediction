import pandas as pd
import pickle 
import numpy as np 

#https://www.dataquest.io/blog/tutorial-add-column-pandas-dataframe-based-on-if-else-condition/
#https://stackoverflow.com/questions/13413590/how-to-drop-rows-of-pandas-dataframe-whose-value-in-a-certain-column-is-nan
#https://stackoverflow.com/questions/25055712/pandas-every-nth-row

separate_data_streams = {
    "temp_hum": ['Air_TempC_Avg', 'Air_TempC_Max', 'Air_TempC_Min', 'Relative_Humidity_Avg', 'Relative_Humidity_Max', 'Relative_Humidity_Min'],
    "rain": ['Ppt_mm_Tot'],
    "wind_speed": ['WS_ms_300cm_Avg', 'WS_ms_300cm_Max', 'WS_ms_150cm_Avg', 'WS_ms_150cm_Max', 'WS_ms_75cm_Avg', 'WS_ms_75cm_Max'],
    "wind_direction": ['WinDir_mean_Resultant', 'WinDir_Std_Dev'],
}

features = ['Air_TempC_Avg', 'Air_TempC_Max', 'Air_TempC_Min', 'Relative_Humidity_Avg', 'Relative_Humidity_Max', 'Relative_Humidity_Min',
'Ppt_mm_Tot', 'WS_ms_300cm_Avg', 'WS_ms_300cm_Max', 'WS_ms_150cm_Avg', 'WS_ms_150cm_Max', 'WS_ms_75cm_Avg', 'WS_ms_75cm_Max',
'WinDir_mean_Resultant', 'WinDir_Std_Dev']

sub_features = ['Air_TempC_Avg', 'Air_TempC_Max', 'Air_TempC_Min', 'Relative_Humidity_Avg', 'Relative_Humidity_Max',
 'Relative_Humidity_Min', 'Ppt_mm_Tot']

key = ["Date_datetime"]
consequent = ["frost"]
npp_named_sites = ['npp_c_cali', 'npp_c_grav', 'npp_c_sand', 'npp_g_basn', 'npp_g_ibpe', 'npp_g_summ', 'npp_m_nort', 'npp_m_rabb', 'npp_m_well', 'npp_p_coll', 'npp_p_smal', 'npp_p_tobo', 'npp_t_east', 'npp_t_tayl', 'npp_t_west']



def create_formatted_csv_from_jornada_df(name, df):
    #Get only the columns we need - features plus Date/Datetime
    keep_cols =  features + key
    modified_features = sub_features + key 
    try:
        df = df[keep_cols]
    except Exception as e:
        print(e)
        df = df[modified_features]
    #Make the next frost column
    df['frost'] = np.where(df["Air_TempC_Min"] <= 0, 1, 0)
    save_name = f"frost_csvs/{name}.csv"
    df.to_csv(save_name)


def make_set():
    for site_name in npp_named_sites:
        pathname = f"pickled_datasets/{site_name}.pkl"
        with open(pathname, "rb") as f:
            site = pickle.load(f)
        create_formatted_csv_from_jornada_df(site_name, site)

#make_set()


def make_shifted_csvs():
    for name in npp_named_sites:
        path = f"frost_csvs/old/{name}.csv"
        df = pd.read_csv(path)
        df["frost"].shift(-1)
        df = df[df["frost"].notna()]
        save_name = f"frost_csvs/{name}.csv"
        df.to_csv(save_name)

#make_shifted_csvs()



cases = {
    4481: {"index": 0},
    3719: {"index": 1},
    1292: {"index": 2},
    2327:{"index": 3},
    5018: {"index": 4},
    6009: {"index": 5},
    1820: {"index": 6},
    2332: {"index": 7},
    4255: {"index": 8},
    1191: {"index": 9},
    1959: {"index": 10},
    553: {"index": 11},
    3631: {"index": 12},
    2738: {"index": 13},
    818: {"index": 14},
    1590: {"index": 15},
    55: {"index": 16},
    4283: {"index": 17},
    5693: {"index": 18},
    5442: {"index": 19},
    3524: {"index": 20},
    4684: {"index": 21},
    5837: {"index": 22},
    1231: {"index": 23},
    6227: {"index": 24},
    985: {"index": 25},
    3930: {"index": 26},
    2267: {"index": 27},
    4573: {"index": 28},
    5983: {"index": 29},
    2272: {"index": 30},
    6246: {"index": 31},
    5607: {"index": 32},
    1900: {"index": 33},
    3694: {"index": 34},
    1785: {"index": 35},
    1018: {"index": 36},
    251: {"index": 37}
}


case_list = [4481, 3719, 1292, 2327, 5018, 6009, 1820, 2332, 4255, 1191, 1959, 553, 3631, 2738, 818, 1590, 55, 4283, 5693, 5442, 3524, 4684, 5837, 1231, 6227, 985, 3930, 2267, 4573, 5983, 2272, 6246, 5607, 1900, 3694, 1785, 1018, 251]
def replace_errant_char(case_list):
    for case in case_list:
        df = pd.read_csv(f"vital_csvs/{case}.csv")
        df.columns = df.columns.str.replace("[/]", "_")
        df.to_csv(f"vital_csvs/{case}.csv")

#eplace_errant_char(case_list) 

#df.columns = df.columns.str.replace("[()]", "_")


def resample_cases(case_list):
    for case in case_list:
        df = pd.read_csv(f"vital_csvs/{case}.csv")
        #Resample to every 10 seconds. Maybe not ideal, but should take down amount of data 
        df = df.iloc[::10, :] 
        df.to_csv(f"vital_csvs/{case}_resampled.csv")

#esample_cases(case_list)