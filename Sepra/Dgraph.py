import osmnx as ox
import networkx as nx
import pickle

WALK_SPEED = 1.4
BUS_SPEED = 40 / 3.6
TAXI_SPEED = 50 / 3.6

BUS_COST = 500
TAXI_COST = 5000

bus_routes = {
    "bus1": {
        "interval": 15,
        "stops": [
            ("bus_11", 30.293556, 57.085553 , 480),
            ("bus_12", 30.293264, 57.078815 , 485),
            ("bus_13", 30.292371, 57.072765 , 490),
            ("bus_14", 30.290954, 57.066992 , 495),
            ("bus_15", 30.289319, 57.059975 , 500),
            ("bus_16", 30.288031, 57.052624 , 505)
        ]
    },
    "bus2": {
        "interval": 30,
        "stops": [
            ("bus_21", 30.277205, 57.031676 , 480),
            ("bus_22", 30.268781, 57.041771 , 485),
            ("bus_23", 30.256100, 57.097405 , 490),
            ("bus_24", 30.257905, 57.103542 , 495),
            ("bus_25", 30.256140, 57.107705 , 500)
        ]
    },
    "bus3": {
        "interval": 30,
        "stops": [
            ("bus_31", 30.292875, 57.088577 , 480),
            ("bus_32", 30.281539, 57.084850 , 485),
            ("bus_33", 30.275030, 57.089715 , 490),
            ("bus_34", 30.270045, 57.093193 , 495),
            ("bus_35", 30.262928, 57.099389 , 500),
            ("bus_36", 30.257999, 57.104530 , 505),
            ("bus_37", 30.256031, 57.107975 , 510)

        ]
    },
    "bus4": {
        "interval": 20,
        "stops": [
            ("bus_41", 30.286904, 57.049716 , 480),
            ("bus_42", 30.285864, 57.045072 , 485),
            ("bus_43", 30.284900, 57.041155 , 490),
            ("bus_44", 30.284217, 57.038102 , 495),
            ("bus_45", 30.283013, 57.032866 , 500),
            ("bus_46", 30.278510, 57.017524 , 505),
            ("bus_47", 30.272900, 57.001179 , 510),
            ("bus_48", 30.270217, 56.993130 , 515),
            ("bus_49", 30.262750, 56.971877 , 520)
        ]
    },
    "bus5": {
        "interval": 30,
        "stops": [
            ("bus_51", 30.286904, 57.049716 , 480),
            ("bus_52", 30.285864, 57.045072 , 485),
            ("bus_53", 30.284900, 57.041155 , 490),
            ("bus_54", 30.284217, 57.038102 , 495),
            ("bus_55", 30.283013, 57.032866 , 500),
            ("bus_56", 30.278510, 57.017524 , 505),
            ("bus_57", 30.272900, 57.001179 , 510),
            ("bus_58", 30.281710, 56.994417 , 515),
            ("bus_59", 30.289440, 56.988504 , 520),
            ("bus_59a", 30.296862, 56.980585 ,525),
            ("bus_59b", 30.305681, 56.970996 ,530)
        ]
    },
    "bus6": {
        "interval": 30,
        "stops": [
            ("bus_61", 30.290493, 57.061216 , 480),
            ("bus_62", 30.294815, 57.057554 , 485),
            ("bus_63", 30.299178, 57.053883 , 490),
            ("bus_64", 30.303714, 57.050014 , 495),
            ("bus_65", 30.305449, 57.048575 , 500),
            ("bus_66", 30.308577, 57.045916 , 505),
            ("bus_67", 30.314091, 57.041257 , 510)
        ]
    },
    "bus7": {
        "interval": 30,
        "stops": [
            ("bus_71", 30.301313, 57.060615 , 480),
            ("bus_72", 30.299491, 57.062014 , 485),
            ("bus_73", 30.297584, 57.063164 , 490),
            ("bus_74", 30.292099, 57.067025 , 495),
            ("bus_75", 30.290356, 57.068251 , 500),
            ("bus_76", 30.286805, 57.070736 , 505),
            ("bus_77", 30.283629, 57.072924 , 510),
            ("bus_78", 30.277083, 57.077472 , 515),
            ("bus_79", 30.274120, 57.079592 , 520),
            ("bus_79a",30.274103, 57.079597 , 525),
            ("bus_79b",30.262840, 57.087432 , 530)
        ]
    },
    "bus8": {
        "interval": 30,
        "stops": [
            ("bus_81", 30.243818, 57.075795 , 480),
            ("bus_82", 30.251065, 57.079560 , 485),
            ("bus_83", 30.258306, 57.083596 , 490),
            ("bus_84", 30.260932, 57.082092 , 495),
            ("bus_85", 30.273936, 57.075627 , 500),
            ("bus_86", 30.277081, 57.077469 , 505),
            ("bus_87", 30.283624, 57.072912 , 510),
            ("bus_88", 30.286840, 57.070703 , 515),
            ("bus_89", 30.291196, 57.068638 , 520)
        ]
    },
    "bus9": {
        "interval": 30,
        "stops": [
            ("bus_91", 30.294599, 57.086388 , 480),
            ("bus_92", 30.309102, 57.087547 , 490),
            ("bus_93", 30.315593, 57.085043 , 500)
        ]
    }
}

taxi_routes = [
    ("taxi_s1", "taxi_e1", 30.287257, 57.053020, 30.294121, 57.086703),
    ("taxi_s2", "taxi_e2", 30.286883, 57.052424, 30.257772, 57.103490),
    ("taxi_s3", "taxi_e3", 30.287246, 57.051251, 30.262595, 56.971470),
    ("taxi_s4", "taxi_e4", 30.286911, 57.051307, 30.266294, 57.009142),
    ("taxi_s5", "taxi_e5", 30.290177, 57.061496, 30.315434, 57.040092),
    ("taxi_s6", "taxi_e6", 30.294145, 57.086651, 30.295653, 57.067546),
    ("taxi_s7", "taxi_e7", 30.293668, 57.087556, 30.291462, 57.125687),
    ("taxi_s8", "taxi_e8", 30.293668, 57.087556, 30.309915, 57.094041)
]
        
def create_osmGraph():
    G_drive = ox.load_graphml("Graphes/kerman_drive.graphml20")
    G_walk  = ox.load_graphml("Graphes/kerman_walk.graphml20")

    return G_drive , G_walk

def nearest_drive(G_drive ,lat, lon):
    return ox.nearest_nodes(G_drive, lon, lat)

def nearest_walk(G_walk,lat, lon):
    return ox.nearest_nodes(G_walk, lon, lat)

def walk_layer(G, D, node_osm):
    for u in D.nodes:
        for v in D.nodes:
            if u == v or D.has_edge(u,v):
                continue

            dist = nx.shortest_path_length(
            G,
            node_osm[u],
            node_osm[v],
            weight="length")

            if dist < 1500:
                time = dist/WALK_SPEED
                D.add_edge(u,v,mode="walk",distance=dist,cost=0,time=time)
                D.add_edge(v,u,mode="walk",distance=dist,cost=0,time=time)

def bus_layer(G,G_walk,D,node_osm):
    for route in bus_routes.values():
        interval = route["interval"]
        stops = route["stops"]

        for i in range(len(stops) - 1):
            u, _, _ , start = stops[i]
            v, _, _ , start1 = stops[i + 1]

            dist = nx.shortest_path_length(
                G_walk,
                node_osm[u],
                node_osm[v],
                weight="length"
            )

            D.add_edge(
                u,v,
                mode="bus",
                distance=dist,
                cost=BUS_COST,
                time=dist/BUS_SPEED,
                interval=interval,
                start=start1
            )
            D.add_edge(
                v,u,
                mode="bus",
                distance=dist,
                cost=BUS_COST,
                time=dist/BUS_SPEED,
                interval=interval,
                start=start1
            )

def taxi_layer(G_walk, D, node_drive, node_walk, taxi_routes, max_walk=300):
    drops = []
    for s, e, slat, slon, elat, elon in taxi_routes:

        path_drive = nx.shortest_path(G_drive, node_drive[s], node_drive[e])
        num_drops = 5  
        step = max(1, len(path_drive)//num_drops)
        drop_nodes = path_drive[::step]
        drops += drop_nodes

        for drop_node in drop_nodes:
            D.add_node(drop_node)
            node_walk[drop_node] = ox.nearest_nodes(G_walk, G_drive.nodes[drop_node]["x"], G_drive.nodes[drop_node]["y"])
            node_drive[drop_node] = ox.nearest_nodes(G_drive, G_drive.nodes[drop_node]["x"], G_drive.nodes[drop_node]["y"])

        ls = [s] + drop_nodes + [e]
        for i in range(1 ,len(ls)):
            u , v = ls[i-1] , ls[i]
            dist = dist = nx.shortest_path_length(G_drive, node_drive[u], node_drive[v], weight='length')
            time_sec = dist / TAXI_SPEED
            D.add_edge(u,v, mode='taxi', distance=dist, time=time_sec, cost=TAXI_COST)
            D.add_edge(v,u, mode='taxi', distance=dist, time=time_sec, cost=TAXI_COST)

        for drop_node in drop_nodes:    
            drop_walk_node = ox.nearest_nodes(G_walk, G_drive.nodes[drop_node]["x"], G_drive.nodes[drop_node]["y"])

            for target in D.nodes:
                if target in ls or target in drops:
                    continue

                target_walk_node = node_walk[target]
                dist = nx.shortest_path_length(G_walk, drop_walk_node, target_walk_node, weight='length')
                if dist <= max_walk:
                    time_sec = dist / WALK_SPEED
                    D.add_edge(drop_node, target, mode='walk', distance=dist, time=time_sec, cost=0)

def save_real_path(D , G_walk , G_drive , node_walk , node_drive):
    real = {}
    for u in D.nodes:
        for v in D.nodes:
            if u == v or  not D.has_edge(u,v):
                continue
            
            edge_data = D.get_edge_data(u, v)
            mode = edge_data.get('mode')

            if mode == 'walk' or mode == 'bus':
                p = nx.shortest_path(G_walk, node_walk[u], node_walk[v], weight="length")
                G_use = G_walk
            else:
                p = nx.shortest_path(G_drive, node_drive[u], node_drive[v], weight="length")
                G_use = G_drive

            coords = [(G_use.nodes[n]["y"], G_use.nodes[n]["x"]) for n in p]
            real[(u,v)] = coords

    with open('Graphes/real_paths.pkl', 'wb') as f:
        pickle.dump(real, f)

G_drive , G_walk = create_osmGraph()
D = nx.DiGraph()

node_drive = {}
node_walk = {}

for r in bus_routes.values():

    for n, lat, lon , _ in r["stops"]:
        D.add_node(n)
        node_drive[n] = nearest_drive(G_drive,lat, lon)
        node_walk[n]  = nearest_walk(G_walk,lat, lon)

for s, e, slat, slon, elat, elon in taxi_routes:
        D.add_node(s)
        D.add_node(e)
        node_drive[s] = nearest_drive(G_drive ,slat, slon)
        node_drive[e] = nearest_drive(G_drive ,elat, elon)
        node_walk[s]  = nearest_walk(G_walk ,slat, slon)
        node_walk[e]  = nearest_walk(G_walk ,elat, elon)

bus_layer(G_drive,G_walk,D,node_walk)

walk_layer(G_walk,D,node_walk)

taxi_layer(G_walk, D, node_drive, node_walk, taxi_routes)

save_real_path(D , G_walk , G_drive , node_walk , node_drive)

nx.write_graphml(D, 'Graphes/Dgraph.graphml')

with open('Graphes/node_drive.pkl', 'wb') as f:
        pickle.dump(node_drive, f)

with open('Graphes/node_walk.pkl', 'wb') as f:
        pickle.dump(node_walk, f)