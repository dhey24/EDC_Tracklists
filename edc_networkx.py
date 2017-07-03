import csv
import networkx as nx
import re
import matplotlib.pyplot as plt

G = nx.Graph()

with open("ALL_Tracklists_enriched.csv", 'rb') as infile:
	reader = csv.reader(infile)
	headers = reader.next()
	for header in headers:
		print headers.index(header), header
	"""
	0 
	1 track
	2 artist
	3 track_artist
	4 track_title
	5 track_remix
	6 track_basic
	7 artist_basic
	"""

	set_artists = []
	track_basics = []

	for row in reader:
		set_artist = row[2]
		if set_artist not in set_artists:
			set_artists.append(set_artist)
		
		track_basic = row[6]
		if track_basic not in track_basics:
			track_basics.append(track_basic)

		#was the set artist involved in creating the track
		if set_artist.lower() in row[3].lower():
			c_type = "created & played"
		else:
			c_type = "played"
		G.add_edge(set_artist, track_basic, connection_type=c_type, 
				   track_info=set_artist+": "+row[1])

		edges = []
		og_edge = (set_artist, track_basic)
		
		#split out all the different artists involved with making the track
		artists = re.split(r" feat. | ft. | & | vs. ", row[3])
		#tie all the artists involved to the track
		for artist in artists:
			if (artist, track_basic) != og_edge:
				edges.append((artist, track_basic))
		
		for e in edges:
			G.add_edge(e[0], e[1], connection_type="created",
					   track_info=set_artist+": "+row[1])

#add attributes to nodes
for n in G:
	if n in set_artists:
		G.node[n]['type'] = "set_artist"
	elif n in track_basics:
		G.node[n]['type'] = "track_basic"
	else:
		G.node[n]['type'] = "artist"

fig1 = plt.figure(figsize=(10,10))
fig1.add_subplot(111)
#pos = nx.draw_spring(G, iterations=100, with_labels=True)
pos = nx.spring_layout(G, iterations=100)
nx.set_node_attributes(G, 'pos', pos)

#plt.show()
#plt.savefig("network.png")

#write to csv for Tableau
with open("EDC_Network.csv", "wb") as outfile:
	writer = csv.writer(outfile)
	writer.writerow(['node',
					 'pos_x',
					 'pos_y',
					 'path_order',
					 'connection',
					 'connection_type',
					 'track_info',
					 'node_type'])
	for e in G.edges_iter():
		path_order = 1
		for n in e:
			row = ([n,
					G.node[n]['pos'][0],
					G.node[n]['pos'][1],
					path_order,
					e[0] + ' - ' + e[1],
					G[e[0]][e[1]]['connection_type'],
					G[e[0]][e[1]]['track_info'],
					G.node[n]['type']])
			writer.writerow(row)
			path_order += 1


