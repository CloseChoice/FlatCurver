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

class DataAcquisition:
  """An Utility class for data acquisition."""

  def fetch_bundesland_rki(self, bundesland:str="Hamburg") -> pandas.DataFrame:
    """
    Fetch Covid-19-Cases a bundesland from 
    https://experience.arcgis.com/experience/478220a4c454480e823b17327b2bf1d4/page/page_0/
    
    Args:
        bundesland: written like displayed on the website, a string
    Returns:
        a Dataframe containing all historical data from a bundesland
        cols = ['date','AnzahlFall']
    """
    
    # build query url
    url_endpoint = "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/RKI_COVID19/FeatureServer/0/query"

    params = {
        'f': 'json', 
        'where': f'Bundesland=\'{bundesland}\'',
        'returnGeometry': 'false',
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'ObjectId,AnzahlFall,Meldedatum',
        'orderByFields': 'Meldedatum asc',
        'resultOffset': 0,
        'resultRecordCount': 2000,
        'cacheHint': "true"    
    }

    url_query = f"{url_endpoint}?{urllib.parse.urlencode(params)}"
    print(url_query)

    # get data from api
    with urllib.request.urlopen(url_query) as url:
        data = json.loads(url.read().decode())['features']
    
    # convert timestamps and format data into a DataFrame
    data_list = [
        (datetime.datetime.fromtimestamp(x['attributes']['Meldedatum'] / 1e3), x['attributes']['AnzahlFall']) 
        for x in data
    ]

    df = pandas.DataFrame(data_list, columns=['date', 'AnzahlFall'])

    return df

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
    Fetch Covid-19-Cases for a bundeland from 
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

    df_all_collumns = ['date']
    for bundesland in df_info['Bundesland']:
      df_all_collumns.append(f'{bundesland}:morgenpost:confirmed')
      df_all_collumns.append(f'{bundesland}:morgenpost:recovered')
      df_all_collumns.append(f'{bundesland}:morgenpost:deaths')
      df_all_collumns.append(f'{bundesland}:rki:infections')
      df_all_collumns.append(f'{bundesland}:rki:deaths')
      df_all_collumns.append(f'{bundesland}:info:population')
      print(bundesland)

    df_all = pandas.DataFrame(columns=df_all_collumns)
    return df_all


if __name__ == "__main__":
  data_acquisition = DataAcquisition()
  df = data_acquisition.fetch_all_data()
  df.to_csv('dataset.csv', index = False)