import glob
import pprint
import re
import csv

#lists all the filepaths that contain a csv
path_list = glob.glob('./Ultra18CSVs/*.csv')
pprint.pprint(path_list)

header = ['track', 'stage', 'artist']

#open new csv to write all the csvs to
with open("ALL_tracklists_UMF18.csv", 'wb') as outfile:
	writer = csv.writer(outfile)
	writer.writerow(header)
	for path in path_list:
		artist = path.split('/')[-1].split('_UMF18.')[0] #Note the wk2 tag
		with open(path, 'rb') as infile:
			reader = csv.reader(infile)
			for row in reader:
				row.append(artist)
				writer.writerow(row)
