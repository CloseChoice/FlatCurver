"""Fetch historical covid-19 data from multpile sources."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# system packages
import urllib
import json
import datetime
import io

# additional packages
import pandas
import numpy as np

def fetch_infection_data_from_rki(bundesland:str="Hamburg",offset=0):
    """
    Fetch Covid-19-Cases from 
    https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4/page/page_0/
    
    Args:
        bundesland: written like displayed on the website, a string
    Returns:
        a Dataframe containing all historical infections data of a bundesland
    """
    
    url_endpoint = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query"
    params = {
        'f': 'json', 
        'where': f'Bundesland=\'{bundesland}\'',
        'returnGeometry': 'false',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'ObjectId,AnzahlFall,Meldedatum,Geschlecht,Altersgruppe',
        'orderByFields': 'Meldedatum asc',
        'resultOffset': offset,
        'resultRecordCount': 2000,
        'cacheHint': "true"    
    }

    url_query = f"{url_endpoint}?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url_query) as url:
        data = json.loads(url.read().decode())['features']
    
    data_list = [
        (datetime.datetime.fromtimestamp(x['attributes']['Meldedatum'] / 1e3), x['attributes']['AnzahlFall'],x['attributes']['Geschlecht'],x['attributes']['Altersgruppe'],bundesland) 
        for x in data
    ]
    
    df = pandas.DataFrame(data_list, columns=['Meldedatum', 'Neuinfektionen', 'Geschlecht','Altersgruppe','Bundesland'])

    if len(data_list)>= 2000:
        df = df.append(fetch_infection_data_from_rki(bundesland,offset+2000))
    
    return df

def fetch_death_data_from_rki(bundesland:str="Hamburg",offset=0):
    """
    Fetch Covid-19-Cases from 
    https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4/page/page_0/
    
    Args:
        bundesland: written like displayed on the website, a string
    Returns:
        a Dataframe containing all historical infections data of a bundesland
    """
    
    url_endpoint = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query"
    params = {
        'f': 'json', 
        'where': f'Bundesland=\'{bundesland}\' AND AnzahlTodesfall>0',
        'returnGeometry': 'false',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'ObjectId,AnzahlTodesfall,Meldedatum,Geschlecht,Altersgruppe',
        'orderByFields': 'Meldedatum asc',
        'resultOffset': offset,
        'resultRecordCount': 2000,
        'cacheHint': "true"    
    }

    url_query = f"{url_endpoint}?{urllib.parse.urlencode(params)}"

    with urllib.request.urlopen(url_query) as url:
        data = json.loads(url.read().decode())['features']
    
    data_list = [
        (datetime.datetime.fromtimestamp(x['attributes']['Meldedatum'] / 1e3), x['attributes']['AnzahlTodesfall'],x['attributes']['Geschlecht'],x['attributes']['Altersgruppe'],bundesland) 
        for x in data
    ]
    
    df = pandas.DataFrame(data_list, columns=['Meldedatum', 'Todesfaelle', 'Geschlecht','Altersgruppe','Bundesland'])

    if len(data_list)>= 2000:
        df = df.append(fetch_death_data_from_rki(bundesland,offset+2000))
    
    return df


flatten = lambda l: [item for sublist in l for item in sublist]

def get_all_dates_sorted(all_death_data,all_infection_data):
    infections_dates = set(all_infection_data.Meldedatum.unique())
    death_dates =  set(all_death_data.Meldedatum.unique())
    all_dates = list(infections_dates.union(death_dates))
    all_dates.sort()
    return all_dates

def get_pivoted_country_data(all_death_data,all_infection_data):
    dates = get_all_dates_sorted(all_death_data,all_infection_data)
    bundeslaender = ["Baden-Württemberg","Nordrhein-Westfalen","Bayern","Hessen","Berlin",
                "Niedersachsen","Sachsen","Rheinland-Pfalz","Brandenburg","Hamburg","Schleswig-Holstein"
                ,"Thüringen","Mecklenburg-Vorpommern","Bremen","Saarland","Sachsen-Anhalt"]

    grouped_infection_data = all_infection_data.groupby(["Meldedatum","Bundesland"])
    grouped_death_data = all_death_data.groupby(["Meldedatum","Bundesland"])
    
    data = []
    for date in dates:
        row = [date]
        for bland in bundeslaender:
            try:
                i_value = grouped_infection_data.get_group((date,bland)).sum()
                row= row +[i_value['Neuinfektionen']]
            except(KeyError):
                row= row +[0]
            try:
                i_value = grouped_death_data.get_group((date,bland)).sum()
                row= row +[i_value['Todesfaelle']]
            except(KeyError):
                row= row +[0]
        data = data + [row]
    
    columns = ["Datum"]
    columns = columns + flatten([[f"{bland}:RKI:Neuinfektionen",f"{bland}:RKI:Todesfaelle"] for bland in bundeslaender])
    
    df = pandas.DataFrame(data,columns=columns)
    
    for bland in bundeslaender:
        df[f'{bland}:RKI:Summe_Infektionen']= df[f'{bland}:RKI:Neuinfektionen'].cumsum()
        df[f'{bland}:RKI:Summe_Todesfaelle']= df[f'{bland}:RKI:Todesfaelle'].cumsum()
        # remove deaths from infections
        df[f'{bland}:RKI:Summe_Infektionen']= df.apply(lambda row: row[f'{bland}:RKI:Summe_Infektionen'] - row[f'{bland}:RKI:Summe_Todesfaelle'] , axis = 1)

    return df

class DataAcquisition:
  """An Utility class for data acquisition."""

  def fetch_rki_data_mergable (self) -> pandas.DataFrame:
    rki_infection_data = fetch_infection_data_from_rki()
    rki_death_data = fetch_death_data_from_rki()
    return get_pivoted_country_data(rki_death_data,rki_infection_data)

  def fetch_germany_morgenpost(self) -> pandas.DataFrame:
    """
    Fetch Covid-19-Cases for Germany from 
    https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/
    
    Args:

    Returns:
        a Dataframe containing all historical data from a bundesland
        cols = ['date','confirmed','recovered', 'deaths']
    """
    # download current history csv file
    url_query = 'https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/data/Coronavirus.history.v2.csv'
        
    with urllib.request.urlopen(url_query) as url:
        csv_string = url.read().decode()

    # read csv from string
    df = pandas.read_csv(io.StringIO(csv_string))

    return df

  def fetch_bundesland_morgenpost(self, bundesland:str="Hamburg") -> pandas.DataFrame:
    """
    Fetch Covid-19-Cases for a bundesland from 
    https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/
    
    Args:
        bundesland: written like displayed on the website, a string
    Returns:
        a Dataframe containing all historical data from a bundesland
        cols = ['date','confirmed','recovered', 'deaths']
    """
    df = self.fetch_germany_morgenpost()

    # filter by bundesland
    df_bundesland = df[df['label']==bundesland]

    # drop unnecessary collumns
    df_bundesland = df_bundesland[['date','confirmed','recovered', 'deaths']]

    return df_bundesland

  def load_general_stats(self, path:str="bundeslaender.csv") -> pandas.DataFrame:
    """
    Extracts bundesland statistical data from a csv file
    
    Args:
        path: path to bundesland csv, a string
    Returns:
        a Dataframe containing all historical data from a bundesland
        cols = ['date','confirmed','recovered', 'deaths']
    """

    return pandas.read_csv(path)

  def fill_days_after_breakout(self, df, df_info, threshold:int=100) -> pandas.DataFrame:
    """
    finds day of outbreak by comparing with a threshold and calcs DaysAfterOutbreak
    
    Args:
      df: historical data for each bundesland, a Dataframe
      threshold: number of infections threshold for outbreak definition

    Returns:
        a Dataframe containing all historical data from a bundesland
    """
    for bundesland in df_info['Bundesland']:
      df[f'{bundesland}:morgenpost:days_after_outbreak'] = df[f'{bundesland}:morgenpost:confirmed'].apply(lambda x: x>threshold).cumsum()
      
    for bundesland in df_info['Bundesland']:
      df[f'{bundesland}:RKI:days_after_outbreak'] = df[f'{bundesland}:RKI:Summe_Infektionen'].apply(lambda x: x>threshold).cumsum()

    return df

  def round_data(self, df, df_info, exactitude:int=10) -> pandas.DataFrame:
    """
    finds day of outbreak by comparing with a threshold and calcs DaysAfterOutbreak
    
    Args:
      df: historical data for each bundesland, a Dataframe
      exactitude: round(value / exactitude) * exactitude, a int

    Returns:
        a Dataframe containing all historical data from a bundesland
    """
    for bundesland in df_info['Bundesland']:
      df[f'{bundesland}:morgenpost:confirmed'] = df[f'{bundesland}:morgenpost:confirmed'].apply(lambda v: np.round(v/exactitude)*exactitude)

    return df

  def fetch_all_data(self) -> pandas.DataFrame:
    """
    merges all data together into one big csv
    
    Args:

    Returns:
        a Dataframe containing all historical data from a bundesland
        cols = ['date','{bundesland}:{source}:{value}','{bundesland}:info:population']
        source = ['rki', 'morgenpost']
    """
    df_info = self.load_general_stats()
    
    collecting_df =  bland_df = self.fetch_bundesland_morgenpost(df_info['Bundesland'][0])
    collecting_df.columns = ["Datum"]+[f"{df_info['Bundesland'][0]}:morgenpost:{c}" for c in collecting_df.columns if c != "date"]
    collecting_df['Datum'] = collecting_df['Datum'].astype('datetime64[ns]')

    for bundesland in df_info['Bundesland'][1:]:
      bland_df = self.fetch_bundesland_morgenpost(bundesland)
      bland_df.columns = ["Datum"]+[f"{bundesland}:morgenpost:{c}" for c in bland_df.columns if c != "date"]
      bland_df['Datum'] = bland_df['Datum'].astype('datetime64[ns]')
      collecting_df = bland_df.merge(collecting_df,how="outer",on="Datum",suffixes=("",""))

    df_rki = self.fetch_rki_data_mergable()

    collecting_df = collecting_df.merge(df_rki,how="outer",on="Datum",suffixes=(False,False))

    collecting_df.fillna(value=0) # Fill every None field from the outer joins with zeroes

    self.round_data(collecting_df, df_info)

    self.fill_days_after_breakout(collecting_df, df_info)

    return collecting_df


if __name__ == "__main__":
  data_acquisition = DataAcquisition()
  df = data_acquisition.fetch_all_data()
  df.to_csv('dataset.csv', index = False)
