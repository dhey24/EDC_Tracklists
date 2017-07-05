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
#counts of songs played per set
df_piv = df.pivot_table(values='track', columns='track_basic',
						index=['artist'],
					    aggfunc=lambda x:x.value_counts().count(), 
					    fill_value=0)
df.set_index('artist', inplace=True)  #simplifies joins later


#create clusters
n_clusters = 10
kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(df_artist_piv)
df_artist_piv['cluster'] = kmeans.labels_

#how many artists per cluster
print df_artist_piv.groupby('cluster').size()


#join the clusters back to the original dataset
df_merged=df.merge(df_artist_piv, how='left', left_index=True, right_index=True)

#do not need 1000 columns in the final dataset
cols = df.columns.values
cols = np.append(cols, 'cluster')
df_merged = df_merged[cols]

df_merged.to_csv("ALL_Tracklists_enriched_clustered.csv")