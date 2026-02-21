🚦 Sepra
Multimodal Time-Dependent Urban Routing Engine

A backend routing engine for multimodal urban transportation integrating pedestrian, bus, and taxi networks with time-dependent cost modeling.

📌 Overview

Sepra is a backend routing engine designed for medium-sized cities with limited smart transportation infrastructure.
It integrates multiple transportation modes into a unified directed graph and computes optimal routes based on time and cost.

The system is built with a custom time-aware Dijkstra variant and supports:

🚶 Pedestrian routing

🚌 Public bus network with interval-based scheduling

🚖 Taxi network with dynamic drop points

⏱ Time-dependent traffic adjustment

💰 Cost-aware route optimization

🧠 Core Features
🔹 Multimodal Graph Integration

Separate pedestrian and driving graphs built from OpenStreetMap data

Unified directed graph for multimodal routing

Dynamic edge injection for taxi and bus layers

🔹 Time-Dependent Routing

Travel time varies based on departure hour

Bus waiting time calculated using service intervals

Traffic factor applied during peak hours

🔹 Cost-Aware Optimization

Combined time + monetary cost scoring

Supports configurable weighting

Extendable to multi-objective routing

🔹 Taxi Drop-Point Heuristic

Generates intermediate drop nodes along driving path

Connects to walkable graph within radius constraint

Reduces unnecessary walking distance

🔹 Robust Input Handling

Coordinate parsing with Persian/English support

Geographic bounding validation

Graceful fallback routing mode

🏗 Architecture
Client → Flask API → Routing Engine
                          │
                          ├── G_walk  (OSM pedestrian graph)
                          ├── G_drive (OSM driving graph)
                          └── D       (Multimodal directed graph)
Engine Layers

Walk Layer

Bus Layer (interval-based schedule modeling)

Taxi Layer (dynamic route injection)

Custom Time-Aware Dijkstra

⚙️ Tech Stack

Python

Flask

NetworkX

OSMnx

OpenStreetMap Data

📊 Routing Strategy

The routing engine:

Maps user coordinates to nearest graph nodes

Expands multimodal graph dynamically

Applies time-dependent weight adjustments

Executes custom Dijkstra algorithm

Returns:

Ordered path

Estimated travel time

Estimated cost

Segment breakdown

📈 Optimization Model

Edge weight is computed as:

effective_weight = base_time × traffic_factor + monetary_cost_weight

Where:

traffic_factor depends on departure hour

Bus waiting time = interval − (arrival_time % interval)

Taxi cost = base_fee + distance_rate × distance

🧪 Testing

Unit tests cover:

Bus waiting time calculation

Traffic factor adjustment

Coordinate validation

Dijkstra path correctness

Run tests:

pytest tests/
🚀 How to Run
pip install -r requirements.txt
python app.py

API endpoint:

POST /route

Example request:

{
  "origin": "30.2839,57.0834",
  "destination": "30.2941,57.0678",
  "departure_time": "08:30"
}
🎯 Engineering Highlights

Designed stateful routing engine architecture

Implemented time-dependent weight modeling

Built multimodal graph from raw OSM data

Created dynamic taxi-drop heuristic layer

Developed fallback routing mechanism for robustness

📌 Future Improvements

True state-space time-dependent Dijkstra

Multi-objective Pareto optimization

Real timetable-based bus modeling

Contraction Hierarchies for performance

Production-ready deployment (Gunicorn + Nginx)

💼 Resume Description (Short Version)

Designed and implemented a multimodal time-dependent urban routing engine integrating pedestrian, bus, and taxi networks using NetworkX and custom Dijkstra variants. Implemented traffic-aware cost modeling and dynamic taxi drop-point heuristics for medium-sized city routing.

![Screenshot 2026-02-17 181722](https://github.com/user-attachments/assets/c9fd9a95-a26d-4ee7-9f4d-94eff4f542d2)
