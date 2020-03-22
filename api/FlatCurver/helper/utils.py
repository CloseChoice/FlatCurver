import pandas as pd

def arrange_dates (indict,timesteps):
    inseries = pd.Series(indict,index=pd.to_datetime([*indict], format='%Y-%m-%d'))
    # create dict of last timestep
    enddate = inseries.index[0]+pd.to_timedelta(timesteps-1,unit="days")
    # create resampled timeseries
    inseries = inseries.resample("1d").fillna("ffill")
    #cut or extend series according to timesteps given
    if enddate in inseries.index:
        outseries = inseries[:enddate]
    else:
        # assign last value of series to last timestep wanted by the user
        endentry = {enddate:inseries[-1]}
        inseries = pd.concat([inseries,pd.Series(endentry)])
        # fill up
        outseries = inseries.resample("1d").fillna("ffill")
    return outseries

