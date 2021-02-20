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
        url = "https://api.artic.edu/api/v1/sounds/search?limit=100&fields=artwork_ids,title"
        r = requests.post(url,headers=headers,json=searchqry)
        r.raise_for_status()
        sounds = r.json()
        if sounds['pagination']['total_pages'] > 1:
            pprint.pprint(sounds['pagination'])
            dataset = dataset + sounds['data']
            pagect = int(sounds['pagination']['total_pages'])
            for i in range(2,pagect + 1):
                url = f"https://api.artic.edu/api/v1/sounds/search?limit=100&fields=artwork_ids,title&page={i}"
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

    pprint.pprint(dataset)


if __name__ == "__main__":
    main(sys.argv)