import csv
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import re

def decrement_cutoff(df, cutoff):
	name = df.name
	print "\n" + str(name) + ", Cutoff = " + str(cutoff)
	print str(name) + " shape before:"
	print df.shape
	df[df > 0] = 1
	df = df.loc[:, (df.sum() > cutoff)]
	print str(name) + " shape after:"
	print df.shape
	df.name = name

	return df


def cluster_df(df, n_clusters=2, artist_cutoff=6, track_cutoff=5):
	#counts of artists played per set
	df_artist_piv = df.pivot_table(values='track', columns='artist_basic', 
								   index=['artist'],
								   aggfunc=lambda x:x.value_counts().count(), 
								   fill_value=0)
	#feature reduction... no tracks that were not played by less than 4 artists
	df_artist_piv.name = "Artist"
	num_cols = 0
	while num_cols == 0 and artist_cutoff >= 1:
		df_artist_piv_new = decrement_cutoff(df_artist_piv, artist_cutoff)
		num_cols = len(df_artist_piv_new.columns)
		if num_cols == 0:
			artist_cutoff += -1
		else:
			df_artist_piv = df_artist_piv_new

	#counts of songs played per set
	df_piv = df.pivot_table(values='track', columns='track_basic',
							index=['artist'],
						    aggfunc=lambda x:x.value_counts().count(), 
						    fill_value=0)
	#feature reduction... no tracks that were not played by less than 4 artists
	df_piv.name = "Track"
	num_cols = 0
	while num_cols == 0 and track_cutoff >= 0:
		df_piv_new = decrement_cutoff(df_piv, track_cutoff)
		num_cols = len(df_piv_new.columns)
		if num_cols == 0:
			track_cutoff += -1
		else:
			df_piv = df_piv_new

	#join tracks and artists features
	if track_cutoff >= 0:
		df_m=df_piv.merge(df_artist_piv, how='left', left_index=True, right_index=True)
	else: 
		df_m = df_artist_piv
	#drop ID columns
	try:
		del df_m['ID']
	except KeyError:
		print "No ID column..."

	#do not want to cluster on less than 4 columns
	if len(df_m.columns) < 6:
		raise ValueError

	#create clusters
	n_clusters = max(2, int((len(df_m.index.unique())/3)**(1/2.0)))
	#n_clusters = max(2, int((len(df_m.columns)/2)**(1/2.0)))
	kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init=100).fit(df_m)
	df_m['cluster'] = kmeans.labels_
	#print df_m['cluster']
	for cluster in range(n_clusters):
		print "\nCluster " + str(cluster) + ":"
		print df_m[df_m['cluster'] == cluster].index.unique()
 
	#label clusters
	terms = df_m.columns.values
	order_centroids = kmeans.cluster_centers_.argsort()[:,::-1]
	df_m['label'] = "None"
	for i in range(n_clusters):
		label = None
		for ind in order_centroids[i, :5]:
			if label is None:
				label = terms[ind]
			else:
				label += ", " + terms[ind]
		df_m.loc[df_m.cluster == i, ['label']] = label 

	#how many artists per cluster
	df_m['label_new'] = df_m['cluster'].map(str) + ' - ' + df_m['label']
	print df_m.groupby('label_new').size()
	
	#find biggest cluster stats
	c_idxmax = df_m.groupby('cluster').size().idxmax()
	c_maxval = df_m.groupby('cluster').size().max()

	df.set_index('artist', inplace=True)  #simplifies joins later

	#join the clusters back to the original dataset
	df_merged=df.merge(df_m, how='left', left_index=True, right_index=True)

	#do not need 1000 columns in the final dataset
	cols = df.columns.values
	cols = np.append(cols, 'cluster')
	df_merged = df_merged[cols]

	return df_merged, c_idxmax, c_maxval, artist_cutoff, track_cutoff


def main():
	#df = pd.read_csv("../ALL_Tracklists_enriched.csv")
	artist_cutoff=14
	track_cutoff=10
	df = pd.read_csv("./ALL_Tracklists_enriched_remixrows.csv")

	c = 0
	c_maxval = 11
	df_final = None
	while c_maxval > 10 and artist_cutoff > 0:
		try:
			df_merged, c_idxmax, c_maxval, artist_cutoff, track_cutoff =  \
					cluster_df(df, 
		    				   artist_cutoff=artist_cutoff, 
		    				   track_cutoff=track_cutoff)
			#add the smaller clusters to the final df
			df_toadd = df_merged[df_merged['cluster'] != c_idxmax]
			remaining_clusters = df_toadd.cluster.unique()
			toss_back = [c_idxmax]
			min_size = 5
			#number final clusters correctly
			for i in remaining_clusters:
				if len(df_toadd[df_toadd['cluster'] == i].index.unique()) >= min_size or artist_cutoff == 1:
					df_toadd['cluster'][df_toadd['cluster'] == i] = c
					c += 1
				else:
					toss_back.append(i)
					df_toadd = df_toadd[df_toadd['cluster'] != i]
					print "Tossing back %s" % (str(i))
			#add to final df
			if df_final is None:
				df_final = df_toadd
			else:
				df_final = pd.concat([df_final, df_toadd])

		except ValueError:
			print "EXCEPTION: NOT ENOUGH FEATURES AT THIS LEVEL"

		artist_cutoff += -1
		track_cutoff += -1
		df = df_merged.reset_index()
		df = df[df['cluster'].isin(toss_back)]
		del df['cluster']

	#add the last cluster
	df_toadd = df_merged[df_merged['cluster'] == c_idxmax]
	df_toadd['cluster'] = c
	df_final = pd.concat([df_final, df_toadd])

	#drop remix rows
	print "\nshape before:"
	print df_final.shape
	df_final = df_final[df_final['remix_row'] == "Original"]
	print "shape after:"
	print df_final.shape

	#print df_final.groupby('cluster', group_keys=True).size()
	for cluster in df_final.cluster.unique():
		print "\nCluster " + str(cluster) + ":"
		print df_final[df_final['cluster'] == cluster].index.unique()

	df_final.to_csv("ALL_Tracklists_enriched_clustered.csv")


if __name__ == '__main__':
	main()