import csv
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import re


def cluster_df(df, n_clusters=2, artist_cutoff=6, track_cutoff=5):
	#counts of artists played per set
	df_artist_piv = df.pivot_table(values='track', columns='artist_basic', 
								   index=['artist'],
								   aggfunc=lambda x:x.value_counts().count(), 
								   fill_value=0)
	#feature reduction... no artists that were not played by less than 4 artists
	print "\n Artists, Cutoff = " + str(artist_cutoff)
	print "Artists shape before:"
	print df_artist_piv.shape
	df_artist_piv[df_artist_piv > 0] = 1
	df_artist_piv = df_artist_piv.loc[:, (df_artist_piv.sum() > artist_cutoff)]
	print "Artists shape after:"
	print df_artist_piv.shape

	#counts of songs played per set
	df_piv = df.pivot_table(values='track', columns='track_basic',
							index=['artist'],
						    aggfunc=lambda x:x.value_counts().count(), 
						    fill_value=0)
	#feature reduction... no tracks that were not played by less than 4 artists
	print "\n Tracks, Cutoff = " + str(track_cutoff)
	print "Tracks shape before:"
	print df_piv.shape
	df_piv[df_piv > 0] = 1
	df_piv = df_piv.loc[:, (df_piv.sum() > track_cutoff)]
	print "Tracks shape after:"
	print df_piv.shape

	#join tracks and artists features
	df_m=df_piv.merge(df_artist_piv, how='left', left_index=True, right_index=True)
	#drop ID columns
	del df_m['ID']

	#create clusters
	n_clusters = 2
	kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init=1).fit(df_m)
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

	return df_merged, c_idxmax, c_maxval


def main():
	#df = pd.read_csv("../ALL_Tracklists_enriched.csv")
	artist_cutoff=6
	track_cutoff=5
	df = pd.read_csv("./ALL_Tracklists_enriched_remixrows.csv")

	c = 0
	c_maxval = 11
	while c_maxval > 10 and track_cutoff >= 1:
		df_merged, c_idxmax, c_maxval = cluster_df(df, 
							    				   artist_cutoff=artist_cutoff, 
							    				   track_cutoff=track_cutoff)
		
		
		#add the smaller clusters to the final df
		df_toadd = df_merged[df_merged['cluster'] != c_idxmax]
		if c == 0:
			df_toadd['cluster'] = c
			df_final = df_toadd
		else:
			df_toadd['cluster'] = c
			df_final = pd.concat([df_final, df_toadd])

		c += 1
		artist_cutoff += -1
		track_cutoff += -1
		df = df_merged.reset_index()
		df = df[df['cluster'] == c_idxmax]
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

	print df_final.groupby('cluster').size()
	
	df_final.to_csv("ALL_Tracklists_enriched_clustered.csv")


if __name__ == '__main__':
	main()