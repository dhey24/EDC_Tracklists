import glob
import pprint
import re
import csv

#lists all the filepaths that contain a csv
path_list = glob.glob('./*.csv')
pprint.pprint(path_list)

header = ['track', 'artist']

#open new csv to write all the csvs to
with open("ALL_tracklists.csv", 'wb') as outfile:
	writer = csv.writer(outfile)
	writer.writerow(header)
	for path in path_list:
		artist = path.split('/')[-1].split('.')[0]
		with open(path, 'rb') as infile:
			reader = csv.reader(infile)
			for row in reader:
				row.append(artist)
				writer.writerow(row)
