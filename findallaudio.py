from io import FileIO
import os
import subprocess
import requests
import pprint
import time
import json
import urllib.parse
import csv
from PIL import Image
import re
import math
import moviepy.editor
import moviepy.Clip
import mutagen
import ffmpeg
import sys
import pickle
from pathlib import Path
import argparse

def main(argv):
	pprint.pprint(argv)
	parser = argparse.ArgumentParser(description='Create videos from all art with audio tour info',
		exit_on_error=False)
	parser.add_argument('--force-refresh',action='store_true',required=False,
					help='Forces a refresh of the dataset against the API, if not specified' \
						'will use locally cached dataset')
	args = parser.parse_args()
	# search for all audio stops

	searchqry = {
		"query": {
			"bool": {
				"must": {
					"match": {
						"title": "Audio stop"
					}
				},
				"must": {
					"exists": {
						"field": "artwork_ids"
					}
				}
			}
		}
	}
	dataset = []
	p = Path("dataset.dmp")
	if p.exists() == False or args.force_refresh == True:
		headers = {'user-agent': 'art-institute-browse/wgoulet@gmail.com'}
		url = "https://api.artic.edu/api/v1/sounds/search?limit=100&fields=artwork_ids,title,id,api_link"
		r = requests.post(url,headers=headers,json=searchqry)
		r.raise_for_status()
		sounds = r.json()
		if sounds['pagination']['total_pages'] > 1:
			pprint.pprint(sounds['pagination'])
			dataset = dataset + sounds['data']
			pagect = int(sounds['pagination']['total_pages'])
			for i in range(2,pagect + 1):
				url = f"https://api.artic.edu/api/v1/sounds/search?limit=100&fields=artwork_ids,title,id,api_link&page={i}"
				r = requests.post(url,headers=headers,json=searchqry)
				r.raise_for_status()
				results = r.json()
				dataset = dataset + results['data']

			# write dataset to object; we'll only refresh this if explicitly asked by users
			with open('dataset.dmp','wb') as dumpfile:
				pickle.dump(dataset,dumpfile)
	else:
		with open('dataset.dmp','rb') as dumpfile:
			dataset = pickle.load(dumpfile)

	#print.pprint(dataset)

	# To minimize API calls, we will query the API in batches of 20

	count = 0
	querystring = ""
	artworks = []
	p = Path("artworkdata.dmp")
	if p.exists() == False or args.force_refresh == True:
		for entry in dataset:
			count += 1
			querystring += f"{str(entry['artwork_ids'][0])},"
			if count % 20 == 0:
				querystring = querystring.rstrip(',')
				pprint.pprint(querystring)
				searchqry = {
					"ids": querystring
				}
				pprint.pprint(searchqry)
				headers = {'user-agent': 'art-institute-browse/wgoulet@gmail.com'}
				url = "https://api.artic.edu/api/v1/artworks"
				r = requests.post(url,headers=headers,json=searchqry)
				r.raise_for_status()
				artworks = artworks + r.json()['data']
				querystring = ""    
		with open("artworkdata.dmp","wb") as artdump:
			pickle.dump(artworks,artdump)
	else:
		with open("artworkdata.dmp","rb") as artdump:
			artworks = pickle.load(artdump)
	#pprint.pprint(artworks)
	# Create id index map of both the sound dataset and artworks dataset for
	# easy lookups/iteration

	idataset = {}
	for e in dataset:
		idataset[e['id']] = e

	iartworks = {}
	for e in artworks:
		iartworks[e['id']] = e

	headers = {'user-agent': 'art-institute-browse/wgoulet@gmail.com'}
	combinedset = []
	p = Path("combineddata.dmp")
	if p.exists() == False or args.force_refresh == True:
		for e in idataset:
			for id in idataset[e]['artwork_ids']:
				if id in iartworks.keys():
					if len(iartworks[id]['artist_ids']) == 0:
						continue
					url = f"https://api.artic.edu/api/v1/agents/{iartworks[id]['artist_ids'][0]}"
					r = requests.get(url,headers=headers)
					r.raise_for_status()
					artistinfo = r.json()
					combinedset = combinedset + [{"audio":idataset[e],"artwork":iartworks[id],"artist":artistinfo['data']}]
					with open("combineddata.dmp","wb") as combineddump:
						pickle.dump(combinedset,combineddump)
	else:
		with open("combineddata.dmp","rb") as combineddump:
			combinedset = pickle.load(combineddump)

	for fullentry in combinedset:
		url = fullentry['audio']['api_link']
		r = requests.get(url,headers=headers)
		r.raise_for_status()
		audiodata = r.json()
		url = audiodata['data']['content']
		r = requests.get(url,headers=headers)
		r.raise_for_status()
		audio = r.content
		audfname = f"{fullentry['artist']['title']}-{fullentry['artwork']['title']}-audiostop.mp3"
		file = open(audfname,"wb")
		file.write(audio)
		file.close()
	pprint.pprint(idataset)
if __name__ == "__main__":
	main(sys.argv)