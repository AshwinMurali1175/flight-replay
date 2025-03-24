# Flight Replay Web Application
This project is a web-based application designed to replay aircraft flights from TLOG files. The app visualizes the flight path on an interactive map, displays altitude and coordinates, and provides playback controls with adjustable speeds.

## Features

- Visualize flight path on an interactive map.
- Show aircraft altitude and coordinates in real-time.
- Play, pause, and control replay speed (1x, 5x, 10x).
  
### Flight-replay

## Create a project file in your preferred location
- I've created it in desktop and created a virtual environment to keep the files more organised using the following commands
```bash
cd ~/Desktop
```
```bash
mkdir flight_replay #to create the directory
```
```bash
cd flight_replay
```
```bash
python3 -m venv venv #to create virtual environment
```
```bash
source venv/bin/activate
```
## Install the required packages in the terminal
```bash
pip install pymavlink flask folium
```
# Create the extract_tlog.py python file
```bash
nano extract_tlog.py
```
- Write the code below to extract the data from the .tlog file into a .json file
```python
import json
import matplotlib.pyplot as plt
from pymavlink import mavutil

def extract_tlog(tlog_path, json_path):
    # Open the tlog file
    mav = mavutil.mavlink_connection(tlog_path)

    # Create an empty list to store flight data
    flight_data = []

    while True:
        # Read the next message
        msg = mav.recv_match()
        if not msg:
            break

        # Collect GPS data (assuming it is GPS_RAW_INT or similar)
        if msg.get_type() == 'GPS_RAW_INT':
            # Extract relevant data
            gps_data = {
                'time': msg.time_usec / 1e6,  # Convert microseconds to seconds
                'lat': msg.lat / 1e7,  # Convert to degrees
                'lon': msg.lon / 1e7,  # Convert to degrees
                'alt': msg.alt / 1000  # Convert to meters
            }
            flight_data.append(gps_data)

    # Write data to a JSON file
    with open(json_path, 'w') as f:
        json.dump(flight_data, f, indent=4)

    # Plot the flight path using matplotlib
    plot_flight_path(flight_data)

def plot_flight_path(flight_data):
    # Extract latitude and longitude for plotting
    latitudes = [entry['lat'] for entry in flight_data if 'lat' in entry]
    longitudes = [entry['lon'] for entry in flight_data if 'lon' in entry]

    # Create a plot of the flight path
    plt.figure(figsize=(8, 6))
    plt.plot(longitudes, latitudes, marker='o', linestyle='-', color='b', markersize=3)
    plt.title('Flight Path')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True)
    plt.show()

# Call the function
extract_tlog('001_assessment_flight.tlog', 'flight_data.json')
```
# Make sure to add the .tlog file in this flight_replay project file to be able to extract the data
# Extract Flight Data from TLOG
- Convert the .tlog file into a flight_data.json file for playback
```bash
  python3 extract_tlog.py
  ```
- This will create a flight_data.json file containing the extracted flight data

## Create the Web App
- Create app.py
```bash
  nano app.py
```
- Write the code below to run and edit your web app HTML file without being overwritten

```python
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
  ```
## Set Up Templates folder and Map File
- The web app requires a templates directory with a map.html file for rendering the map interface
```bash
mkdir templates
```
- Generate the map.html File
```bash
nano templates/map.html
```
- Edit the JavaScript HTML code in this file with codes matching the requirements

```html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <title>Flight Path Replay</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body, html {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }

        #controls {
            background: white;
            padding: 10px;
            display: flex;
            justify-content: center;
            gap: 10px;
            position: relative;
            z-index: 1000;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }

        #map {
            flex: 1;
            width: 100%;
        }

        #info {
            text-align: center;
            padding: 10px;
            font-size: 16px;
            background: white;
            box-shadow: 0px -2px 5px rgba(0, 0, 0, 0.2);
        }

        .aircraft-icon {
            width: 40px;
            height: 40px;
            transform-origin: center;
            transition: transform 0.2s linear;
        }
    </style>
</head>
<body>
    <div id="controls">
        <button onclick="play()">Play</button>
        <button onclick="pause()">Pause</button>
        <button onclick="setSpeed(1)">1x</button>
        <button onclick="setSpeed(5)">5x</button>
        <button onclick="setSpeed(10)">10x</button>
    </div>

    <div id="map"></div>
            
    <p id="info">Time: -- | Coordinates: -- | Altitude: --</p>
         
    <script>
        // Initialize Map
        const map = L.map('map').setView([0, 0], 13);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
            
        let flightData = [];  
        let currentIndex = 0;
        let replaySpeed = 1000;
        let replayInterval = null;
        let aircraftMarker = null;
        let aircraftIconElement = null;
        let bluePath = null;
        let redPath = L.polyline([], { color: 'red', weight: 3 }).addTo(map); // Red trail
            
        // Load Flight Data
        async function loadFlightData() {
            const response = await fetch('/flight_data.json');
            flightData = await response.json();
    
            if (flightData.length === 0) {
                alert('No flight data found!'); 
                return;
            }
        
            // Center map on the first point
            map.setView([flightData[0].lat, flightData[0].lon], 15);
    
            // Draw initial flight path in blue
            const coordinates = flightData.map(point => [point.lat, point.lon]);
            bluePath = L.polyline(coordinates, { color: 'blue', weight: 3 }).addTo(map);
    
            // Add aircraft marker with custom HTML icon
            aircraftIconElement = document.createElement('img');
            aircraftIconElement.src = 'https://upload.wikimedia.org/wikipedia/commons/1/1e/Airplane_silhouette.png';
            aircraftIconElement.className = 'aircraft-icon';
        
            const aircraftIcon = L.divIcon({
                className: '', 
                html: aircraftIconElement.outerHTML,
                iconSize: [40, 40],
                iconAnchor: [20, 20],  
            });
        
            aircraftMarker = L.marker([flightData[0].lat, flightData[0].lon], { icon: aircraftIcon }).addTo(map);
        
            // Update initial info
            updateInfo(flightData[0]);
        }
    
        function updateMarker() {
            if (currentIndex < flightData.length) {
                const { lat, lon, time, heading, alt } = flightData[currentIndex];
        
                aircraftMarker.setLatLng([lat, lon]);
                map.panTo([lat, lon]);
                updateInfo(flightData[currentIndex]);
         
                // Rotate aircraft icon based on heading
                const imgElement = aircraftMarker.getElement().querySelector('img');
                if (imgElement && heading !== undefined) {
                    imgElement.style.transform = `rotate(${heading}deg)`; // Fixing the rotation
                }
                
                // Move the trail from blue to red
                const traveledPath = flightData.slice(0, currentIndex + 1).map(point => [point.lat, point.lon]);
                redPath.setLatLngs(traveledPath);
                
                // Remove traveled portion from the blue path
                const remainingPath = flightData.slice(currentIndex).map(point => [point.lat, point.lon]);
                bluePath.setLatLngs(remainingPath);
                
                currentIndex++;
            } else {
                pause();
            }
        }   
        
        function updateInfo(data) {
            const formattedTime = data.time || "--";
            const altitude = data.alt !== undefined ? `${data.alt} m` : "--"; // Accessing alt instead of altitude
            document.getElementById("info").innerText = `Time: ${formattedTime} | Coordinates: (${data.lat}, ${data.lon}) | Altitude: ${altitude}`;
        }    
       
        function play() {
            if (!replayInterval) {
                replayInterval = setInterval(updateMarker, replaySpeed);
            }
        }
                
        function pause() {
            clearInterval(replayInterval);
            replayInterval = null;
        }       
                
        function setSpeed(speed) {
            replaySpeed = 1000 / speed;
            if (replayInterval) {
                pause();
                play();
            }
        }       
                
        loadFlightData();
    </script>
</body>
</html>     

```

## Run the App
```bash
python3 app.py
```
## Open the web app

- Once the app is running, open your browser and go to:

  The displayed web app link = http://127.0.0.1:5000

# You should have a fully functioning web application to play, pause the flight path with speed adjusters of 1x, 5x, 10x while displaying coordinates, altitude and time on a map


  
