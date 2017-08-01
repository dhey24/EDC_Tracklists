from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import requests
import pprint as pp
from fake_useragent import UserAgent
import csv
import re
import time
import random
import pandas as pd


def scrape_tracklist(link, headers, artist, stage):
	"""scrape the tracklists info and write to csv"""
	tracklist = []
	time.sleep(random.randint(0, 5)) #occasionally pause for a few seconds

	page = requests.get(link, headers=headers)
	soup = BeautifulSoup(page.content, "lxml")
	tracks = soup.find_all("div", class_="tlToogleData")

	with open(artist + "_TLwk2.csv", 'wb') as outfile:
		writer = csv.writer(outfile)

		for track in tracks:
			try:
				content = track.meta['content']
				pp.pprint(content)
				#replace unicode characters
				content = re.sub(r'[^\x00-\x7F]+', '*', content) 	
				writer.writerow([content, stage])
				tracklist.append(content)
			except TypeError:
				content = None
				continue

	return tracklist


def scrape_links(search_url, headers, all_artists, artist_meta, 
				 scrape_tracks=True):
	"""1. get all the tracklist URLs on a given page
	   2. navigate to those URLs and scrape the tracklists
	   3. write to csv"""
	page = requests.get(search_url, headers=headers)
	pp.pprint(page)
	soup = BeautifulSoup(page.content, "lxml")
	pages = soup.find_all("div", class_="tlLink")

	if len(pages) == 0:
		print "\nWE GOT BLOCKED?!?!\n"

	for page in pages:
		link = 'https://www.1001tracklists.com' + page.a['href']
		description = page.a.get_text()
		if "Tomorrowland Weekend " in description:
			description = description.split(" @ ")
			artist = description.pop(0)
			description = description[0].split(", ")
			stage = description.pop(0)
			weekend = description.pop(0)
			#only scrape tracklists if it has not been pulled already
			if artist not in all_artists:
				artist = re.sub(r'[^\x00-\x7F]+', '*', artist)
				artist_meta.append({'artist': artist, 
									'stage': stage, 
									'url': link,
									'weekend': weekend})
				all_artists.append(artist)

				print "\n" + artist, weekend + "\n"

				if scrape_tracks:
					scrape_tracklist(link, headers, artist, stage)

	return all_artists, artist_meta


def main():
	all_artists = []
	artist_meta = []

	for i in range(1, 6):
		if i == 1:
			search_url = "https://www.1001tracklists.com/source/fgcfkm/tomorrowland/index.html"
		else:
			search_url = "https://www.1001tracklists.com/source/fgcfkm/tomorrowland/index" + \
						  str(i) + ".html"
		time.sleep(random.randint(5, 15)) #occasionally pause for a few seconds

		ua = UserAgent()
		headers = {'User-Agent': str(ua.random)}

		all_artists, artist_meta = scrape_links(search_url, 
												headers, 
												all_artists, 
												artist_meta,
												scrape_tracks=True)

	#write artist reference metadata to seperate csv
	df = pd.DataFrame.from_dict(artist_meta)
	df.to_csv('Tomorrowland_wk2_artist_meta.csv')

if __name__ == '__main__':
	main()
