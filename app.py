import random
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from deap import base, creator, tools, algorithms
import io

st.set_page_config(layout="wide")
st.title("Vehicle Routing Problem (VRP) Solver - Genetic Algorithm")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("Problem Settings")
    use_custom_locations = st.checkbox("Enter Custom Locations (Lat, Lon)", value=False)
    num_locations = st.slider("Number of Locations", 5, 50, 20)
    num_vehicles = st.slider("Number of Vehicles", 1, 10, 3)
    random_seed = st.number_input("Random Seed", value=42)

# --- Location Generation ---
random.seed(random_seed)
if use_custom_locations:
    st.subheader("Enter Coordinates")
    custom_data = st.text_area("Paste lat, lon (one per line)", "12.97, 77.59\n13.01, 77.64\n13.05, 77.53")
    try:
        locations = [tuple(map(float, line.strip().split(","))) for line in custom_data.strip().splitlines()]
        num_locations = len(locations)
    except:
        st.error("Invalid format. Use: latitude, longitude per line.")
        st.stop()
else:
    locations = [(random.uniform(12.9, 13.1), random.uniform(77.5, 77.7)) for _ in range(num_locations)]

depot = (13.0, 77.6)

# --- Distance Matrix ---
def compute_distance_matrix(locations):
    return np.round([[np.linalg.norm(np.array(a) - np.array(b)) for b in locations] for a in locations], 2)

# --- GA Setup ---
creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("indices", random.sample, range(num_locations), num_locations)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalVRP(individual):
    total_distance = 0
    distances = []
    for i in range(num_vehicles):
        route = [depot] + [locations[individual[j]] for j in range(i, len(individual), num_vehicles)] + [depot]
        vehicle_dist = sum(np.linalg.norm(np.array(route[k+1]) - np.array(route[k])) for k in range(len(route)-1))
        total_distance += vehicle_dist
        distances.append(vehicle_dist)
    balance_penalty = np.std(distances)
    return total_distance, balance_penalty

toolbox.register("evaluate", evalVRP)
toolbox.register("mate", tools.cxPartialyMatched)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

# --- Route Plot ---
def plot_routes(individual):
    fig, ax = plt.subplots()
    for x, y in locations:
        ax.plot(x, y, 'bo')
    ax.plot(depot[0], depot[1], 'rs')
    for i in range(num_vehicles):
        route = [depot] + [locations[individual[j]] for j in range(i, len(individual), num_vehicles)] + [depot]
        xs, ys = zip(*route)
        ax.plot(xs, ys, '-', label=f'Vehicle {i+1}')
    ax.set_title("Optimized Routes")
    ax.legend()
    return fig

# --- Run GA ---
if st.button("Solve VRP"):
    with st.spinner("Optimizing routes..."):
        pop = toolbox.population(n=300)
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)

        algorithms.eaSimple(pop, toolbox, 0.7, 0.2, 300, stats=stats, halloffame=hof, verbose=False)

    st.success("Optimization Complete!")
    fig = plot_routes(hof[0])
    st.pyplot(fig)

    # --- Dynamic Map Plot ---
    st.subheader("Route Map (Approximate)")
    all_coords = pd.DataFrame(locations, columns=["lat", "lon"])
    st.map(all_coords)

    # --- Distance Matrix ---
    st.subheader("Distance Matrix")
    dist_matrix = compute_distance_matrix(locations)
    df_matrix = pd.DataFrame(dist_matrix)
    st.dataframe(df_matrix)

    # --- Export Route as CSV ---
    st.subheader("Export Routes as CSV")
    routes = []
    for i in range(num_vehicles):
        vehicle_locs = [locations[individual] for j, individual in enumerate(hof[0]) if j % num_vehicles == i]
        for idx, loc in enumerate(vehicle_locs):
            routes.append({
                "vehicle": i + 1,
                "stop": idx + 1,
                "lat": loc[0],
                "lon": loc[1]
            })
    df_routes = pd.DataFrame(routes)
    st.dataframe(df_routes)

    csv = df_routes.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "vrp_routes.csv", "text/csv")

