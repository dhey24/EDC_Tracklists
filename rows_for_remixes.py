import csv
import pandas as pd
import re

df = pd.read_csv("../ALL_Tracklists_enriched.csv")
artists = df.artist_basic.unique()

with open("../ALL_Tracklists_enriched.csv", 'rb') as infile:
	reader = csv.reader(infile)

	headers = reader.next()
	headers.append('remix_row')
	for header in headers:
		print headers.index(header), header

	with open("ALL_Tracklists_enriched_remixrows.csv", "wb") as outfile:
		writer = csv.writer(outfile)
		writer.writerow(headers)

		for row in reader:
			row.append("Original")
			writer.writerow(row)	#write basic row
			if len(row[5]) > 2:
				for artist in artists:
					if artist in row[5]:
						print row[2] + " -> " + artist + " --> " + str(row[5])
						row[7] = artist
						row[8] = "Remix"
						writer.writerow(row) #write remix artist row
			
			#rows for featured or vs. artists
			#split out all the different artists involved with making the track
			feats = re.split(r" feat. | ft. | & | vs. ", row[3])
			#tie all the artists involved to the track
			if len(feats) > 1:
				for feat in feats[1:]:
					row[7] = feat
					row[8] = "Feature/VS"
					print "Ft/vs: " + row[2] + " -> " + feat + " --> " + str(row[1])
					writer.writerow(row) #write remix artist row