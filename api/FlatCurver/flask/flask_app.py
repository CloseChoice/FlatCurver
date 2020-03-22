
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/simulate', methods=['POST', 'GET'])
def simulate():
    from FlatCurver.helper.CallPandemy import CallPandemy
    json = request.get_json()
    json_ger = json.pop('Deutschland')
    caller = CallPandemy()
    result_bl = caller.call_simulation_bundeslaender(json, gamma={}, delta={}, timesteps=200)
    result_ger = caller.call_simulation_germany(json_ger, gamma={}, delta={}, timesteps=200)
    result_bl.update(result_ger)
    return result_bl

@app.route('/debug', methods=['POST', 'GET'])
def debug():
    try:
        json = request.get_json()
        return dict(text=str(json))
    except Exception as e:
        return dict(text='ERROR:\n' + str(e))

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=8051, threaded=True)