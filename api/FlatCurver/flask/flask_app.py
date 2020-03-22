
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, jsonify, request, Response
from flask_cors import CORS

import json

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/simulate', methods=['POST', 'GET'])
def simulate():
    from FlatCurver.helper.CallPandemy import CallPandemy
    SIMULATED_TIMESTEPS = 200

    json_data = request.get_json()
    json_ger = json_data.pop('Deutschland')
    caller = CallPandemy()
    result_bl = caller.call_simulation_bundeslaender(json_data, gamma={}, delta={}, timesteps=SIMULATED_TIMESTEPS)
    result_ger = caller.call_simulation_germany(json_ger, gamma={}, delta={}, timesteps=SIMULATED_TIMESTEPS)
    result_bl.update(result_ger)
    return Response(response=json.dumps(result_bl), status=SIMULATED_TIMESTEPS, mimetype="application/json")

@app.route('/debug', methods=['POST', 'GET'])
def debug():
    try:
        json = request.get_json()
        return dict(text=str(json))
    except Exception as e:
        return dict(text='ERROR:\n' + str(e))

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=8051, threaded=True)