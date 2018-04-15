import csv
import pandas as pd
import re


#create the base columns for the dataframe
df = pd.read_csv("./ALL_tracklists_UMF18.csv")
df.columns = ['track_info','stage', 'artist']
df['track'] = df['track_info'].apply(lambda x: x.split(' - ')[1])
df['track_artist'] = df['track_info'].apply(lambda x: x.split(' - ')[0])
df['track_basic'] = df['track'].apply(lambda x: x.split(' (')[0])
df['artist_basic'] = df['track_artist'].apply(lambda x: re.split('( feat. | ft. )', x)[0])
df['track_remix'] = df['track'].apply(lambda x: [re.search('\((.*)\)', x).group(1)] if re.search('\((.*)\)', x) else [])

#find all the unique DJs
artists = df.artist_basic.unique()

#headers for the new CSV, print for debugging
headers = list(df.columns.values)
headers.append('remix_row')
for header in headers:
	print headers.index(header), header

#create csv with a row for each artist involved in the song
with open("ALL_Tracklists_enriched_remixrows_UMF18.csv", "wb") as outfile:
	writer = csv.writer(outfile)
	writer.writerow(headers)

	for index, row in df.iterrows():
		row['remix_status'] = 'Original'
		writer.writerow(row)	#write basic row 
		if len(row['track_remix']) > 0:
			found = False
			for artist in artists:
				if artist in row['track_remix'][0]:
					#print row['artist'] + " -> " + artist + " --> " + str(row['track_remix'])
					row['artist_basic'] = artist
					row['remix_status'] = 'Remix'
					writer.writerow(row) #write remix artist row
					found = True
			#if one of the other DJ's is not the remixer...
			if found == False:
				#delete the remix type strings
				stripped_remix = re.sub('( Mashup| Remix| *Acappella| *Edit|'+ \
										' Blastersmash| Re-Edit| *VIP Mix|'  + \
										' *Bootleg| Mash-Boot| *Vocal Mix|'  + \
										'Dub Mix|Club Mix|VIP| Rework|' + \
										'Instrumental Mix|Re-Crank|Classic Mix)', 
										'', row['track_remix'][0])
				#only write row when there is data, because we are looking for remix artists
				if len(stripped_remix) > 0:
					print row['artist'] + " -> " + stripped_remix + " --> " + str(row['track_remix'])
					row['artist_basic'] = stripped_remix
					row['remix_status'] = 'Remix'
					writer.writerow(row) #write remix artist row
		
		#rows for featured or vs. artists
		#split out all the different artists involved with making the track
		feats = re.split(r" feat. | ft. | & | vs. ", row['track_artist'])
		#tie all the artists involved to the track
		if len(feats) > 1:
			for feat in feats[1:]:
				row['artist_basic'] = feat
				row['remix_status'] = "Feature/VS"
				#print "Ft/vs: " + row['artist'] + " -> " + feat + " --> " + str(row['track_info'])
				writer.writerow(row) #write remix artist row 