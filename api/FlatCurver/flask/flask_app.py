
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
    json_data = request.get_json()
    
    json_data.pop("Deutschland")
    thueringen = json_data.pop("Th\u00fcringen")
    #json_data["Thüringen"] = thueringen
    
    bw = json_data.pop("Baden-W\u00fcrttemberg")
    print(bw)
    #json_data["Baden-Württemberg"] = bw
    #json_data.pop("Baden-W\u00fcrttemberg")
    with open('data.json', 'w') as outfile:
        json.dump(json_data, outfile)

    caller = CallPandemy()
    result = caller.call_simulation_bundeslaender(json_data, gamma={}, delta={}, timesteps=200)

    return Response(response=json.dumps(result), status=200, mimetype="application/json")

@app.route('/debug', methods=['POST', 'GET'])
def debug():
    try:
        json = request.get_json()
        return dict(text=str(json))
    except Exception as e:
        return dict(text='ERROR:\n' + str(e))

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=8051, threaded=True)