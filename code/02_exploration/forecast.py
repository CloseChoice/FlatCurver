import requests
import json
import pandas as pd


def build_payload(df, horizon):
    """ Builds payload for API """
    date = df.date.values.tolist()
    target = df.confirmed.values.tolist()
    payload = {
        'horizon': horizon,
        'data': {
            'date': date,
            'target': target
        }
    }
    return payload


def postprocess(response):
    """ Postprocessing of API response """
    return json.loads(response.text)


# Import data
df = pd.read_csv('././data/Coronavirus.history.v2.csv')

# Data prep
df_model = df[df.parent == 'Deutschland'].sort_values(by=['label', 'date'])

# States
labels = df_model.label.unique()

# Get forecasts
for label in labels:
    print('Predicting {state}'.format(state=label))
    df_forecast = df_model[df_model.label == label]
    payload = build_payload(df_forecast, horizon=1)
    response = requests.post(url='https://us-central1-flatcurver.cloudfunctions.net/forecast', data=json.dumps(payload))
    print(postprocess(response))
