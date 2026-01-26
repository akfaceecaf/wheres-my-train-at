from nyct_gtfs import NYCTFeed
from datetime import datetime
from flask import Flask, jsonify
import json
import os
from dotenv import load_dotenv
app = Flask(__name__)

load_dotenv()
PORT = int(os.getenv("PORT",5000))

with open('./data/stops.json', 'r') as f:
    STOPS = json.load(f)
ROUTES =  ["B", "D", "F", "M","A", "C", "E","G","J", "Z","N", "Q", "R", "W","L","1", "2", "3", "4", "5", "6", "7", "S"]

@app.route("/")
def index():
    return "MTA"


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/mta/<stopId>/<routeId>")
def fetch_train(stopId, routeId):
    current_time = datetime.now()
    try:
        if stopId not in STOPS:
            return jsonify({"error":"invalid stop id"}), 400
        if routeId not in ROUTES: 
            return jsonify({"error":"invalid route id"}), 400
        stop_name = STOPS[stopId]["stop_name"]
        feed = NYCTFeed(routeId) 
        trains = feed.filter_trips(line_id=routeId)
        stop_times = []
        for train in trains:
            for stop in train.stop_time_updates:
                if stop.stop_id == stopId:
                    stop.minutes_away = max(int((stop.arrival - current_time).total_seconds() // 60),0)
                    stop_times.append(stop)
        stop_times.sort(key=lambda a: a.arrival)
        if len(stop_times) == 0:
            return jsonify({
                "routeId": None,
                "stopName": None,
                "arrivalTime": None,
                "minutesAway": None,
            }), 404
        stop_times = stop_times[0]
        print(stop_times)
        return jsonify({
            "routeId": routeId,
            "stopName": stop_name,
            "arrivalTime": int(stop_times.arrival.timestamp()),
            "minutesAway": stop_times.minutes_away,
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error":"failed to fetch MTA data"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=PORT, host="0.0.0.0")