import osmnx as ox
import heapq
import networkx as nx
import pickle

WALK_SPEED = 1.4

BUS_COST = 500
TAXI_COST = 5000

WAIT_TAXI = 10 * 60
BUS_START = 8 * 60
BUS_END = 20 * 60 

bus_routes = {
    "bus1": {
        "interval": 10 ,
        "stops": [
            ("bus_11", 30.293556, 57.085553),
            ("bus_12", 30.293264, 57.078815),
            ("bus_13", 30.292371, 57.072765),
            ("bus_14", 30.290954, 57.066992),
            ("bus_15", 30.289319, 57.059975),
            ("bus_16", 30.288031, 57.052624)
        ]
    },
    "bus2": {
        "interval": 30,
        "stops": [
            ("bus_21", 30.277205, 57.031676),
            ("bus_22", 30.268781, 57.041771),
            ("bus_23", 30.256100, 57.097405),
            ("bus_24", 30.257905, 57.103542),
            ("bus_25", 30.256140, 57.107705)
        ]
    },
    "bus3": {
        "interval": 30,
        "stops": [
            ("bus_31", 30.292875, 57.088577),
            ("bus_32", 30.281539, 57.084850),
            ("bus_33", 30.275030, 57.089715),
            ("bus_34", 30.270045, 57.093193),
            ("bus_35", 30.262928, 57.099389),
            ("bus_36", 30.257999, 57.104530),
            ("bus_37", 30.256031, 57.107975)

        ]
    },
    "bus4": {
        "interval": 15,
        "stops": [
            ("bus_41", 30.286904, 57.049716),
            ("bus_42", 30.285864, 57.045072),
            ("bus_43", 30.284900, 57.041155),
            ("bus_44", 30.284217, 57.038102),
            ("bus_45", 30.283013, 57.032866),
            ("bus_46", 30.278510, 57.017524),
            ("bus_47", 30.272900, 57.001179),
            ("bus_48", 30.270217, 56.993130),
            ("bus_49", 30.262750, 56.971877)
        ]
    },
    "bus5": {
        "interval": 30,
        "stops": [
            ("bus_51", 30.286904, 57.049716),
            ("bus_52", 30.285864, 57.045072),
            ("bus_53", 30.284900, 57.041155),
            ("bus_54", 30.284217, 57.038102),
            ("bus_55", 30.283013, 57.032866),
            ("bus_56", 30.278510, 57.017524),
            ("bus_57", 30.272900, 57.001179),
            ("bus_58", 30.281710, 56.994417),
            ("bus_59", 30.289440, 56.988504),
            ("bus_59a", 30.296862, 56.980585),
            ("bus_59b", 30.305681, 56.970996),
        ]
    },
    "bus6": {
        "interval": 30,
        "stops": [
            ("bus_61", 30.290493, 57.061216),
            ("bus_62", 30.294815, 57.057554),
            ("bus_63", 30.299178, 57.053883),
            ("bus_64", 30.303714, 57.050014),
            ("bus_65", 30.305449, 57.048575),
            ("bus_66", 30.308577, 57.045916),
            ("bus_67", 30.314091, 57.041257)
        ]
    },
    "bus7": {
        "interval": 30,
        "stops": [
            ("bus_71", 30.301313, 57.060615),
            ("bus_72", 30.299491, 57.062014),
            ("bus_73", 30.297584, 57.063164),
            ("bus_74", 30.292099, 57.067025),
            ("bus_75", 30.290356, 57.068251),
            ("bus_76", 30.286805, 57.070736),
            ("bus_77", 30.283629, 57.072924),
            ("bus_78", 30.277083, 57.077472),
            ("bus_79", 30.274120, 57.079592),
            ("bus_79a", 30.274103, 57.079597),
            ("bus_79b", 30.262840, 57.087432)
        ]
    },
    "bus8": {
        "interval": 30,
        "stops": [
            ("bus_81", 30.243818, 57.075795),
            ("bus_82", 30.251065, 57.079560),
            ("bus_83", 30.258306, 57.083596),
            ("bus_84", 30.260932, 57.082092),
            ("bus_85", 30.273936, 57.075627),
            ("bus_86", 30.277081, 57.077469),
            ("bus_87", 30.283624, 57.072912),
            ("bus_88", 30.286840, 57.070703),
            ("bus_89", 30.291196, 57.068638)
        ]
    },
    "bus9": {
        "interval": 30,
        "stops": [
            ("bus_91", 30.294599, 57.086388),
            ("bus_92", 30.309102, 57.087547),
            ("bus_93", 30.315593, 57.085043)
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
    ("taxi_s8", "taxi_e8", 30.293668, 57.087556, 30.309915, 57.094041),
]

def dijkstra(G, start, end, start_time_min):
    pq = []
    counter = 0
    heapq.heappush(pq, (0,0,start_time_min,counter,start,[]))
    visited = {} 

    while pq:
        total_time,total_cost,current_time,_,u,edge_path = heapq.heappop(pq)

        if u in visited and visited[u] <= total_time:
            continue
        visited[u] = total_time

        if u == end:
            return {
                "edge_path": edge_path,
                "time": total_time,
                "cost": total_cost
            }

        for v, data in G[u].items():
            mode = data.get("mode", "walk")
            dist = data.get("distance", 0)
            t = data.get('time')
            c = data.get('cost')
            tf = traffic_factor(current_time)


            if mode == "taxi":
                t = t * tf + WAIT_TAXI
                c = TAXI_COST

            elif mode == "bus":
                if current_time > BUS_END:
                    continue

                if u[4] == v[4]:
                    t *= tf

                else:
                    BUS_START = data.get(start , 480)
                    BUS_INTERVAL = data.get('interval')
                    arrival = current_time
                    if arrival < BUS_START:
                        wait = BUS_START - arrival
                    else:
                        wait = (BUS_INTERVAL - ((arrival - BUS_START) % BUS_INTERVAL)) % BUS_INTERVAL

                    t = wait * 60 + t * tf

            new_edge = {
                "from": u,
                "to": v,
                "mode": mode,
                "time_sec": t,
                "cost": c
            }   
            counter+=1
            heapq.heappush(
                pq,
                (
                    total_time + t,
                    total_cost + c,
                    current_time + int(t / 60),
                    counter,
                    v,
                    edge_path + [new_edge]
                )
            )
            
    return None

def short_path(G,a,b):
    pq = []
    heapq.heappush(pq, (0, a))

    dist = {a: 0}
    prev = {a: None}

    while pq:
        cur_dist, u = heapq.heappop(pq)

        if u == b:
            break

        if cur_dist > dist.get(u, float("inf")):
            continue

        for v, edges in G[u].items():

            edge = list(edges.values())[0]
            w = edge.get('length', 1)
            nd = cur_dist + w

            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if b not in prev:
        return None, float("inf")

    path = []
    cur = b
    while cur:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    return path, dist[b]
        
def create_osmGraph():
    G_drive = ox.load_graphml("Graphes/kerman_drive.graphml20")
    G_walk  = ox.load_graphml("Graphes/kerman_walk.graphml20")
    D = nx.read_graphml('Graphes/Dgraph.graphml')

    return G_drive , G_walk ,D

def nearest_drive(G_drive,lat, lon):
    return ox.nearest_nodes(G_drive, lon, lat)

def nearest_walk(G_walk,lat, lon):
    return ox.nearest_nodes(G_walk, lon, lat)

def add_edge_from_start_end(G, D, node_osm):
    stops = [n for n in D.nodes if n not in ["start", "end"]]

    for s in stops:
        try:
            dist = nx.shortest_path_length(
                G,
                node_osm["start"],
                node_osm[s],
                weight="length")
        except KeyError:
            continue
        if dist < 3000:
            time = dist/WALK_SPEED
            D.add_edge("start",s,mode="walk",distance=dist,cost=0,time=time)

    for s in stops:
        try:
            dist = nx.shortest_path_length(
                G,
                node_osm[s],
                node_osm["end"],
                weight="length")
        except KeyError:
            dist = nx.shortest_path_length(
                G,
                node_osm[int(s)],
                node_osm["end"],
                weight="length")
        if dist < 3000:
            time = dist/WALK_SPEED
            D.add_edge(s,"end",mode="walk",distance=dist,cost=0,time=time)

def real_path(edge_path , save_real , G_walk , G_drive , node_walk , node_drive):
    real = {}
    for edge in edge_path:
        if (edge['from'],edge['to']) in save_real.keys():
            p = save_real[(edge['from'] ,edge['to'])]

        if edge['mode'] == 'walk' or edge['mode'] == 'bus':
            try:
                p = nx.shortest_path(G_walk, node_walk[edge['from']], node_walk[edge['to']], weight="length")
                G_use = G_walk
            except:
                p = nx.shortest_path(G_walk, node_walk[edge['from']], node_walk[int(edge['to'])], weight="length")
                G_use = G_walk
        else:
            p = nx.shortest_path(G_drive, node_drive[edge['from']], node_drive[edge['to']], weight="length")
            G_use = G_drive

        coords = [(G_use.nodes[n]["y"], G_use.nodes[n]["x"]) for n in p]
        real.setdefault(edge['mode'], []).append(coords)

    return real

def snap(start , end , time):
    G = ox.load_graphml("Graphes/snap_drive.graphml20")
    p , dist = short_path(G,start,end)

    tf = traffic_factor(time)
    travel_time_sec = dist / 10 * tf

    total_cost = travel_time_sec + dist/1000 * 15000

    p = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in p]
    
    return p , total_cost / 2.5 , travel_time_sec

def total_cost(edge_path):
    cost , f = 0 , ''
    for edge in edge_path:
        if edge['mode'] == 'walk':
            cost += 0

        elif edge['mode'] == 'bus':
            if f != edge['from'][4]:
                cost += 2500
                f = edge['from'][4]

            elif edge['from'][4] == edge['to'][4]:
                cost += 0

        else:
            if edge['from'].startwith('taxi_s'):
                cost += 15000
            else:
                cost += 0

    return cost

def traffic_factor(h):
    h = h//60
    if 7 <= h < 9 and 13 <= h <= 15:
        return 2
    if 9 <= h < 16:
        return 1.5
    if 16 <= h < 19:
        return 2.5
    return 1.2

G_drive , G_walk , D = create_osmGraph()

with open('Graphes/real_paths.pkl', 'rb') as f:
    save_real = pickle.load(f)

with open('Graphes/node_drive.pkl', 'rb') as f:
    node_drive = pickle.load(f)

with open('Graphes/node_walk.pkl', 'rb') as f:
    node_walk = pickle.load(f)