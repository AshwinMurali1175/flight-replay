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
