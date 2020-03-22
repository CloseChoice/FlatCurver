import pandas as pd


def arrange_dates(dct, timesteps):
    srs = pd.Series(dct, index=pd.to_datetime(list(dct.keys())))
    end_date = srs.index[0] + pd.to_timedelta(timesteps-1, unit="days")
    srs.loc[end_date] = srs.values[-1]
    return srs.resample('1d').pad()


