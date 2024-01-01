import warnings

warnings.filterwarnings("ignore", category=UserWarning, message="Secure coding is not enabled for restorable state")


import re
import pytz
import numpy as np
import pandas as pd
import numpy_ext as npe
import matplotlib.pyplot as plt
import scipy.stats as scist
import statsmodels.formula.api as smf

from pprint import pprint
from datetime import datetime
from datetime import timedelta

from functions import get_primes
from functions import _get_feature_matrix
from functions import classical_roll
from functions import create_datetime_from_week

contract_name_list = []
p_value_list = []
coeff_2_list = []
coeff_3_list = []
coeff_5_list = []
beta_2_list = []
beta_3_list = []
beta_5_list = []

def run_seasonality(contract, contract_df):
    mgrps=contract_df.groupby(by=[contract_df.index.month, contract_df.index.year])
    monthlies=pd.concat([(1+mgrps.get_group(group).cont_ret).cumprod().tail(1)-1 for group in mgrps.groups])
    monthlies=monthlies.loc[sorted(monthlies.index)]

    '''global in-sample seasonality test and portfolio on monthly returns
    '''

    #adjust number of primes here
    X,primes,k=_get_feature_matrix(m=5,n=len(monthlies))
    kwargs={"X_"+str(i):arr for i,arr in zip(range(k),X.T)} 
    df=pd.DataFrame(index=monthlies.index, data={"r":monthlies.values, **kwargs}) 
    multiple_tests={}
    '''sequential regression testing'''
    for j in range(k):
        formula=f"r ~ {' + '.join(['C(' + str(kwarg) +  ')' for kwarg in kwargs.keys() if int(kwarg.split('_')[1]) <= j])}"
        res=smf.ols(formula=formula,data=df).fit()
        j_test={
            "f_test": res.f_pvalue,
            "coeffs": res.params,
            "t_tests": res.pvalues
        }
        multiple_tests[j] = j_test

    fpvals=[multiple_tests[j]["f_test"] for j in range(k)]
    adj_pvals=k/np.sum([1/p for p in fpvals])
    coeff_ps=multiple_tests[k-1]["t_tests"].values[1:]
    coeff_vals=multiple_tests[k-1]["coeffs"].values[1:]
    alpha=1 #ignore to show all in sample graphs

    '''in-sample portfolio construction using the regression model'''
    seasons=np.multiply(np.where(coeff_ps<alpha,1,0),coeff_vals)
    votess = np.array([np.multiply(x,seasons) for x in X])
    positions=np.array([np.sum(votes) for votes in votess])
    print("Contract is: "+contract)
    print("adj-P Value is "+str(round(adj_pvals,3)))
    print("2,3,5 Month p-Values: ")
    print([round(p,3) for p in coeff_ps])
    print("Coefficents:")
    print([round(beta,3) for beta in coeff_vals], "\n")
    df["positions"]=positions
    df["insamp_ret"] = df.r*df.positions
    plt.plot(np.log((1+df.insamp_ret).cumprod()),label="insamp_monthlies")
    plt.title(contract)
    img_name = contract+"_insample.png"
    plt.savefig(img_name)

    '''walkforward classical seasonality test
    based on last 5 years of data, long top 3 months and short bottom 3 months for the next one year period
    '''
    mgrps=contract_df.groupby(by=[contract_df.index.month, contract_df.index.year])
    classical_df=pd.concat([(1+mgrps.get_group(group).cont_ret).cumprod().tail(1)-1 for group in mgrps.groups])
    classical_df=classical_df.loc[sorted(classical_df.index)]
    classical_df=pd.DataFrame(index=classical_df.index,data={"date": classical_df.index, "cont_ret": classical_df.values})
    classical_df["positions"]=np.nan

    if len(classical_df)>12*6:
        rollop=npe.rolling_apply(
            classical_roll, 
            12*6,#5y calibration, 1 year walk
            *classical_df[["date","cont_ret"]].T.values,
            classical_df
        )
        classical_df=classical_df.fillna(0.0)
        classical_df["classical_portfolio"]=classical_df.positions*classical_df.cont_ret
        ret_bnh=classical_df.cont_ret.loc[classical_df.cont_ret != 0].values
        ret_sea=classical_df.classical_portfolio.loc[classical_df.classical_portfolio != 0].values
        shrp_sea=round(np.mean(ret_sea)/np.std(ret_sea)*np.sqrt(12),3)
        shrp_bnh=round(np.mean(ret_bnh)/np.std(ret_bnh)*np.sqrt(12),3)
        
        plt.plot(np.log((1+classical_df.classical_portfolio).cumprod()),label=f"classical_seasonality: {shrp_sea}")
        plt.plot(np.log((1+classical_df.cont_ret).cumprod()),label=f"buy and hold: {shrp_bnh}")
        plt.title(contract)
        plt.legend()

        img_name = contract+"_walkforward.png"
        plt.savefig(img_name)

    contract_name_list.append(contract)
    p_value_list.append(round(adj_pvals,3))
    coeff_2_list.append(round(coeff_ps[0],3))
    coeff_3_list.append(round(coeff_ps[1],3))
    coeff_5_list.append(round(coeff_ps[2],3))
    beta_2_list.append(round(coeff_vals[0],3))
    beta_3_list.append(round(coeff_vals[1],3))
    beta_5_list.append(round(coeff_vals[2],3))

    output_dict = {"Contract":contract_name_list, "P-value":p_value_list,
                "2 Month P-value": coeff_2_list, "3 Month P-value": coeff_3_list,
                "5 Month P-value": coeff_5_list, "2 Month beta": beta_2_list,
                "3 Month beta": beta_3_list, "5 Month beta": beta_5_list}
    return pd.DataFrame(output_dict)

btc_df = pd.read_csv("/Users/aronnyberg/code/quanty2/gateio_data//btc_daily_rets.csv")
btc_df['timestamp'] = pd.to_datetime(btc_df['timestamp'])
btc_df.set_index('timestamp',inplace=True)
btc_df.index = pd.DatetimeIndex(btc_df.index)
btc_df.rename(columns={"vwap": "cont_ret"}, inplace=True)

city_df = pd.read_csv("/Users/aronnyberg/code/quanty2/gateio_data//city_daily_rets.csv")
city_df['timestamp'] = pd.to_datetime(city_df['timestamp'])
city_df.set_index('timestamp',inplace=True)
city_df.index = pd.DatetimeIndex(city_df.index)
city_df.rename(columns={"vwap": "cont_ret"}, inplace=True)

for each in [("BTC", btc_df), ("CITY", city_df)]:
    output_df = (run_seasonality(each[0], each[1]))
    print(output_df)

