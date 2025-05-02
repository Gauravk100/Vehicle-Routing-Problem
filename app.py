import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import os

from dotenv import load_dotenv

load_dotenv()

MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")

def get_route(start, end):
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start[1]},{start[0]};{end[1]},{end[0]}?access_token={MAPBOX_ACCESS_TOKEN}&geometries=geojson"
    response = requests.get(url)
    data = response.json()
    return data


st.title("Vehicle Routing Problem with Mapbox")

# Ask user for the number of locations and vehicles
num_locations = st.number_input("Enter the number of locations (excluding depot):", min_value=1, value=5, step=1)
num_vehicles = st.number_input("Enter the number of vehicles:", min_value=1, value=2, step=1)

# Input for depot location
st.subheader("Depot Location (Start/End Point)")
depot_lat = st.number_input("Depot Latitude:", value=50.0, format="%.6f")
depot_lon = st.number_input("Depot Longitude:", value=10.0, format="%.6f")
depot = (depot_lat, depot_lon)

# Input for each location
locations = []
st.subheader("Locations")
for i in range(num_locations):
    st.write(f"Location {i+1}")
    lat = st.number_input(f"Latitude {i+1}:", key=f"lat_{i}", format="%.6f")
    lon = st.number_input(f"Longitude {i+1}:", key=f"lon_{i}", format="%.6f")
    locations.append((lat, lon))

# Display the locations
st.write("### Locations:")
for i, loc in enumerate(locations):
    st.write(f"Location {i+1}: {loc}")

# Initialize session state for storing routes if it doesn't exist
if 'calculated_routes' not in st.session_state:
    st.session_state.calculated_routes = None

# Plot the locations on a map
m = folium.Map(location=depot, zoom_start=6)

# Add depot marker
folium.Marker(location=depot, popup="Depot", icon=folium.Icon(color='red')).add_to(m)

# Add locations markers
for i, loc in enumerate(locations):
    folium.Marker(location=loc, popup=f"Location {i+1}").add_to(m)

# Display the map with locations
st_folium(m, width=700, height=500, key="initial_map")

# Calculate and plot routes for each vehicle
if st.button("Calculate Routes"):
    m = folium.Map(location=depot, zoom_start=6)
    
    # Add markers again (since we're creating a new map)
    folium.Marker(location=depot, popup="Depot", icon=folium.Icon(color='red')).add_to(m)
    for i, loc in enumerate(locations):
        folium.Marker(location=loc, popup=f"Location {i+1}").add_to(m)
    
    # Assign locations to vehicles (simple round-robin assignment)
    colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 
              'darkblue', 'darkgreen', 'cadetblue', 'pink', 'lightblue', 'lightgreen']
    
    vehicle_routes = []
    
    for vehicle_num in range(1, num_vehicles + 1):
        # Get locations assigned to this vehicle
        vehicle_locations = [depot] + [locations[i] for i in range(vehicle_num - 1, len(locations), num_vehicles)] + [depot]
        
        # Calculate the route for this vehicle
        route_coords = []
        for i in range(len(vehicle_locations) - 1):
            start, end = vehicle_locations[i], vehicle_locations[i + 1]
            route = get_route(start, end)
            
            if route['routes']:
                route_coords.extend([(point[1], point[0]) for point in route['routes'][0]['geometry']['coordinates']])
        
        # Add the vehicle route polyline to the map
        if route_coords:
            folium.PolyLine(
                route_coords, 
                color=colors[vehicle_num % len(colors)], 
                weight=2.5, 
                opacity=1,
                popup=f"Vehicle {vehicle_num}"
            ).add_to(m)
            
            vehicle_routes.append({
                'vehicle_num': vehicle_num,
                'color': colors[vehicle_num % len(colors)],
                'route_coords': route_coords
            })
    
    # Store the routes in session state
    st.session_state.calculated_routes = vehicle_routes
    
    # Display the map with routes
    st_folium(m, width=700, height=500, key="routed_map")

# If we have calculated routes, display them again (to prevent disappearance)
if st.session_state.calculated_routes:
    m = folium.Map(location=depot, zoom_start=6)
    
    # Add markers
    folium.Marker(location=depot, popup="Depot", icon=folium.Icon(color='red')).add_to(m)
    for i, loc in enumerate(locations):
        folium.Marker(location=loc, popup=f"Location {i+1}").add_to(m)
    
    # Add stored routes
    for route in st.session_state.calculated_routes:
        folium.PolyLine(
            route['route_coords'], 
            color=route['color'], 
            weight=2.5, 
            opacity=1,
            popup=f"Vehicle {route['vehicle_num']}"
        ).add_to(m)
    
    st.write("### Calculated Routes:")
    st_folium(m, width=700, height=500, key="persistent_routed_map")     .add_to(m)
    
    st.write("### Calculated Routes:")
    st_folium(m, width=700, height=500, key="persistent_routed_map")     .add_to(m)
    
    st.write("### Calculated Routes:")
    st_folium(m, width=700, height=500, key="persistent_routed_map")     .add_to(m)
    
    st.write("### Calculated Routes:")
    st_folium(m, width=700, height=500, key="persistent_routed_map")     .add_to(m)
    
    st.write("### Calculated Routes:")
    st_folium(m, width=700, height=500, key="persistent_routed_map")
