import pandas as pd
import numpy as np

def get_primes(n):
    #https://stackoverflow.com/questions/2068372/fastest-way-to-list-all-primes-below-n
    """ Returns  a list of primes < n """
    sieve = [True] * n
    for i in range(3,int(n**0.5)+1,2):
        if sieve[i]:
            sieve[i*i::2*i]=[False]*((n-i*i-1)//(2*i)+1)
    return [2] + [i for i in range(3,n,2) if sieve[i]]

def _get_feature_matrix(m,n):
    primes=get_primes(m+1)
    k=len(primes)
    dummies=[]
    for xk in range(k):
        arr=np.zeros(n)
        arr[primes[xk]-1::primes[xk]] = 1
        dummies.append(arr)
    X = np.vstack(dummies).T
    return X,primes,k

def classical_roll(dt,r, classical_df):
    df=pd.DataFrame(index=dt,data={"r":r})
    if not np.isnan(classical_df.at[dt[12*5],"positions"]):
        return
    calibrate_df=df.loc[:dt[12*5]] #first 5 year positions
    mnth_grps=calibrate_df.groupby(by=calibrate_df.index.month)
    mnthlies={grp: np.mean(mnth_grps.get_group(grp).r.values) for grp in mnth_grps.groups}
    mnthlies={k:v for k,v in sorted(mnthlies.items(), key=lambda pair: pair[1]) }
    short,long=list(mnthlies.keys())[:3],list(mnthlies.keys())[-3:]
    positions=[-1 if i.month in short else (1 if i.month in long else 0) for i in dt[12*5:]] #next one year positions
    classical_df["positions"].loc[dt[12*5:]] = positions

    # Function to create a new datetime column based on FY and week numbers
def create_datetime_from_week(row):
    # Assuming the financial year starts on April 1st
    # Calculate the day of the year based on the week and financial year
    day_of_year = (row['Week'] - 1) * 7
    # Create a datetime object
    return pd.to_datetime(f"{row['FY_']}-04-01") + pd.DateOffset(days=day_of_year)