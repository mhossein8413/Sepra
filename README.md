🚦 Sepra
Multimodal Time-Dependent Urban Routing Engine for Kerman

A backend decision engine for multimodal urban routing integrating pedestrian, bus, taxi, and ride-hailing networks using real OpenStreetMap street data.

📌 Project Architecture

The project is divided into three major stages:

Graph Construction (Static Layer)

Routing Algorithm & Dynamic Processing

Web Application Layer

🧱 Stage 1 — Graph Construction (Static Layer)
🗺 Real Street Networks

Two real-world street graphs are constructed using OSMnx and OpenStreetMap data:

🚶 G_walk → Pedestrian network

🚗 G_drive → Driving network

Both graphs are downloaded directly from OpenStreetMap and represent real streets of Kerman, Iran, ensuring realistic routing.

This makes the engine operate on actual city infrastructure instead of synthetic graphs.

🧠 Decision Graph (Multimodal Graph)

A third directed graph D is built as the decision graph.

Nodes include:

🚌 Bus stations

🚖 Taxi stations

Each node in the decision graph is mapped to:

The nearest node in G_walk

The nearest node in G_drive

This mapping enables reconstruction of the exact real-world path after routing.

🔹 Edge Layers in the Decision Graph

The decision graph contains three transportation layers:

🚶 Walking Layer

For every pair of nodes with distance < 1500 meters:

A bidirectional edge is added

Mode = "walk"

Stored attributes:

Distance

Travel time

This creates dense pedestrian connectivity between nearby stations.

🚌 Bus Layer

For every pair of bus stations located on the same route:

A bidirectional edge is added

Mode = "bus"

Stored attributes:

Route distance

Travel time

Ticket cost

Waiting time

Service start time

Waiting time is computed dynamically based on service interval.

🚖 Taxi Layer

Taxi routing is designed with a drop-point heuristic:

Between each origin and destination station,

5 intermediate nodes are generated along the driving path.

These nodes allow flexible drop-off points.

Each intermediate node connects to nearby nodes (< 300m) using walking edges.

Stored attributes are similar to bus edges:

Distance

Travel time

Cost

Waiting/start information

This allows the passenger to get off the taxi optimally before the final node.

⚙️ Stage 2 — Routing Algorithm (Dynamic Layer)
🎯 User Inputs

The system receives three inputs:

Origin

Destination

Departure Time

🔄 Dynamic Graph Expansion

At runtime:

Origin and destination are added to the decision graph.

They are connected via walking edges.

Routing is executed using a custom Dijkstra algorithm.

🧮 Custom Dijkstra Algorithm

Two variations are used:

1️⃣ Time-Cost Optimized Routing

The main routing algorithm uses a customized Dijkstra implementation with a heap.

Edge weights consider:

Travel time

Monetary cost

Traffic factor

Waiting time (for bus)

Cost function:

total_cost = travel_time_sec + dist/1000 * 15000

This enables a combined time + economic optimization strategy.

2️⃣ Distance-Based Routing

A second Dijkstra variation computes shortest path purely based on distance.

🕒 Time-Dependent Adjustments

Traffic factor changes based on departure hour.

Bus waiting time is computed using interval logic.

Travel time dynamically affects total weight.

This introduces real-world temporal behavior into routing.

🗺 Real Path Reconstruction

After the optimal path in the decision graph is found:

Each node’s stored mapping is used.

The exact route is reconstructed from:

G_walk

G_drive

The full real street-level path is generated.

🚘 Alternative Route — Ride-Hailing (Snap)

The same routing pipeline is executed for a ride-hailing option.

A cost function is applied:

total_cost = travel_time_sec + dist/1000 * 15000

This provides users with an alternative route suggestion.

🌐 Stage 3 — Web Application Layer

The system includes a Flask-based backend API.

🔹 Features

Coordinate validation (Persian & English support)

Geographic bounding validation (Kerman area)

Graceful fallback mode

JSON route response

Debug logging

Real-time route computation

🔹 API Flow

Client → Flask API → Routing Engine → JSON Response

Example Request
{
  "origin": "30.2839,57.0834",
  "destination": "30.2941,57.0678",
  "departure_time": "08:30"
}
Example Response

Ordered multimodal path

Total travel time

Total estimated cost

Segment breakdown

🧠 Engineering Highlights

Real OpenStreetMap street integration

Multimodal graph modeling

Layered decision graph architecture

Time-dependent routing

Custom Dijkstra implementation

Taxi drop-point heuristic

Cost-aware optimization

Dynamic graph expansion

Real-world path reconstruction

🛠 Tech Stack

Python

Flask

NetworkX

OSMnx

OpenStreetMap

🚀 Why This Project Is Interesting

This project demonstrates:

Graph modeling

Algorithm customization

Multimodal routing design

Time-aware optimization

System-level architectural thinking

Real urban data integration

It is not a simple API wrapper — it is a custom routing engine.

📌 Resume-Ready Description

Designed and implemented a multimodal time-dependent urban routing engine integrating pedestrian, bus, taxi, and ride-hailing networks using real OpenStreetMap data. Developed a custom Dijkstra-based cost-aware routing algorithm with traffic and waiting-time modeling. Built dynamic graph expansion and real path reconstruction using NetworkX and OSMnx.

![Screenshot 2026-02-17 181722](https://github.com/user-attachments/assets/c9fd9a95-a26d-4ee7-9f4d-94eff4f542d2)
