import osmnx as ox
import networkx as nx
import folium

ox.settings.use_cache = True
ox.settings.log_console = True

center = (30.2835, 57.0835)
dist = 20000

G_walk = ox.graph_from_point(center, dist=dist, network_type="walk")
G_drive = ox.graph_from_point(center, dist=dist, network_type="drive")

ox.save_graphml(G_walk, "kerman_walk.graphml20")
ox.save_graphml(G_drive, "kerman_drive.graphml20")