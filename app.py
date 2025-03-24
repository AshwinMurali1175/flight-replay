from flask import Flask, render_template, send_from_directory, jsonify
import json

app = Flask(__name__)

@app.route('/')
def map_view():
    return render_template("map.html")

@app.route('/flight_data.json')
def flight_data():
    try:
        with open('flight_data.json') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "Flight data not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
