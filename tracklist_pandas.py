import csv
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

df = pd.read_csv("../ALL_Tracklists_enriched.csv")

#counts of artists played per set
df_artist_piv = df.pivot_table(values='track', columns='artist_basic', 
							   index=['artist'],
							   aggfunc=lambda x:x.value_counts().count(), 
							   fill_value=0)
#feature reduction... no artists that were not played by less than 4 artists
print "shape before:"
print df_artist_piv.shape
df_artist_piv[df_artist_piv > 0] = 1
df_artist_piv = df_artist_piv.loc[:, (df_artist_piv.sum() > 4)]
print "shape after:"
print df_artist_piv.shape

#counts of songs played per set
df_piv = df.pivot_table(values='track', columns='track_basic',
						index=['artist'],
					    aggfunc=lambda x:x.value_counts().count(), 
					    fill_value=0)
#feature reduction... no tracks that were not played by less than 4 artists
print "shape before:"
print df_piv.shape
df_piv[df_piv > 0] = 1
df_piv = df_piv.loc[:, (df_piv.sum() > 4)]
print "shape after:"
print df_piv.shape

#join tracks and artists features
df_m=df_piv.merge(df_artist_piv, how='left', left_index=True, right_index=True)

#create clusters
n_clusters = 3
kmeans = KMeans(n_clusters=n_clusters, random_state=0, n_init=1).fit(df_m)
df_m['cluster'] = kmeans.labels_
print df_m['cluster']

#how many artists per cluster
print df_m.groupby('cluster').size()

df.set_index('artist', inplace=True)  #simplifies joins later

#join the clusters back to the original dataset
df_merged=df.merge(df_m, how='left', left_index=True, right_index=True)

#do not need 1000 columns in the final dataset
cols = df.columns.values
cols = np.append(cols, 'cluster')
df_merged = df_merged[cols]

df_merged.to_csv("ALL_Tracklists_enriched_clustered.csv")