from bs4 import BeautifulSoup
from bs4 import UnicodeDammit
import requests
import pprint as pp
from fake_useragent import UserAgent
import csv
import re
import time
import random

#important for scraping to work
ua = UserAgent()
headers = {'User-Agent': str(ua.random)}


def scrape_tracklist(link, headers, artist):
	"""scrape the tracklists info and write to csv"""
	tracklist = []
	time.sleep(random.randint(0, 5)) #occasionally pause for a few seconds

	page = requests.get(link, headers=headers)
	soup = BeautifulSoup(page.content, "lxml")
	tracks = soup.find_all("div", class_="tlToogleData")

	with open(artist + ".csv", 'wb') as outfile:
		writer = csv.writer(outfile)

		for track in tracks:
			try:
				content = track.meta['content']
				pp.pprint(content)
				content = re.sub(r'[^\x00-\x7F]+', '*', content) 	#replace unicode characters
				writer.writerow([content])
				tracklist.append(content)
			except TypeError:
				content = None
				continue

	return tracklist


def scrape_links(search_url, headers, all_artists):
	"""1. get all the tracklist URLs on a given page
	   2. navigate to those URLs and scrape the tracklists
	   3. write to csv"""
	page = requests.get(search_url, headers=headers)
	pp.pprint(page)
	soup = BeautifulSoup(page.content, "lxml")
	pages = soup.find_all("div", class_="tlLink")

	tracklists = {}

	for page in pages:
		link = 'https://www.1001tracklists.com' + page.a['href']
		description = page.a.get_text()
		description = description.split(" @ ")
		artist = description.pop(0)
		description = description[0].split(", ")
		stage = description.pop(0)
		#only scrape tracklists if it has not been pulled already
		if artist not in all_artists:
			tracklists[artist] = {'stage': stage, 'url': link}
			all_artists.append(artist)

			print
			print artist
			print

			scrape_tracklist(link, headers, artist)

	return all_artists

def main():
	all_artists = []

	for i in range(4,5):
		if i == 1:
			search_url = "https://www.1001tracklists.com/source/fgcfkm/tomorrowland/index.html"
		else:
			search_url = "https://www.1001tracklists.com/source/fgcfkm/tomorrowland/index" + \
						  str(i) + ".html"
		time.sleep(random.randint(5, 15)) #occasionally pause for a few seconds
		all_artists = scrape_links(search_url, headers, all_artists) 


if __name__ == '__main__':
	main()
