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

def main(argv):
    print ("hello world")
    pprint.pprint(argv)
    artist = ""
    if len(argv) < 2:
        print("Invalid arguments; usage main.py [artist name]")
    else:
        for i in range(1,len(argv)):
            artist = artist + "{0} ".format(argv[i])
        artist = artist.strip()
    
    print("Searching for artist {0} works".format(artist))
    headers = {'user-agent': 'art-institute-browse/wgoulet@gmail.com'}

    # search only for individual artists
    searchqry = {
        "query": {
            "bool": {
                "must": {
                    "term": {
                        "agent_type_id": 7
                    }
                },
                "filter": {
                    "match": {
                        "title":{
                        "query": "{0}".format(artist),
                        "operator":"AND"
                        }
                    }
                }
            }
        }
    }
    codedqry = urllib.parse.urlencode(searchqry)
    pprint.pprint(codedqry)
    url = "https://api.artic.edu/api/v1/agents/search?limit=100"
    r = requests.post(url,headers=headers,json=searchqry)
    r.raise_for_status()
    agents = r.json()
    pprint.pprint(agents)
    artistid = agents['data'][0]['id']
    pprint.pprint(artistid)

    searchqry = {
        "query": {
            "bool": {
                "must": {
                    "term": {
                        "artist_id": artistid
                    }
                }
            }
        }
    }
    time.sleep(1)
    url = "https://api.artic.edu/api/v1/artworks/search?limit=0"

    r = requests.post(url,headers=headers,json=searchqry)
    r.raise_for_status()
    art = r.json()
    resultsize = art['pagination']['total']
    pages = int(math.ceil(resultsize / 10))
    
    for i in range(1,pages):
        url = "https://api.artic.edu/api/v1/artworks/search?&limit=10&page={0}".format(i)
        r = requests.post(url,headers=headers,json=searchqry)
        r.raise_for_status()
        art = r.json()
        for item in art['data']:
            print(item['title']) 
            print(item['id'])
            # Try and find an audio stop file for the artwork
            searchqry = {
                "query": {
                    "bool": {
                        "must": {
                            "term": {
                                "artwork_ids": item['id']
                            }
                        }
                    }
                }
            }
            time.sleep(1)
            url = "https://api.artic.edu/api/v1/sounds/search?limit=10"
            r = requests.post(url,json=searchqry,headers=headers)
            r.raise_for_status()
            sounds = r.json()
            audlen = 0
            audfname = None
            audfclip = None
            for sound in sounds['data']:
                if re.match('audio stop.*',sound['title'],re.IGNORECASE):
                    pprint.pprint(sound['title'])
                    url = sound['api_link']
                    time.sleep(1)
                    r = requests.get(url,headers=headers)
                    r.raise_for_status()
                    soundinfo = r.json()
                    url = soundinfo['data']['content']
                    time.sleep(1)
                    r = requests.get(url,headers=headers)
                    r.raise_for_status()
                    audio = r.content
                    audfname = "{0}-{1}-audiostop.mp3".format(artist,item['title'])
                    file = open(audfname,"wb")
                    file.write(audio)
                    file.close()
                    audinfo = mutagen.File(audfname)
                    audlen = math.ceil(audinfo.info.length)


            imagesearch = "https://api.artic.edu/api/v1/artworks/{0}?fields=id,title,image_id".format(item['id'])
            r = requests.get(imagesearch,headers=headers)
            r.raise_for_status()
            imageinfo = r.json()
            imageurl = imageinfo['config']['iiif_url']
            imageid = imageinfo['data']['image_id']
            imageparams = "/full/1686,/0/default.jpg"
            fullurl = "{0}/{1}{2}".format(imageurl,imageid,imageparams)
            r = requests.get(fullurl,headers=headers)
            try:
                r.raise_for_status()
                
                img = r.content
                imgname = "{0}-{1}.jpg".format(artist,item['title'])
                vname = "{0}-{1}.mp4".format(artist,item['title'])
                fvname = "{0}-{1}-all.mp4".format(artist,item['title'])
                file = open("{0}-{1}.jpg".format(artist,item['title']),"wb")
                file.write(img)
                file.close()
                if audfname != None:
                    subprocess.run(['ffmpeg','-loop','1','-i', imgname,"-c:v","libx264",
                     '-t',"{0}".format(audlen),'-pix_fmt','yuv420p','-vf','scale=320:240',vname])
                    subprocess.run(['ffmpeg','-i',audfname,'-i',vname,fvname])
            except:
                print("Unable to get image for {0}".format(item['title']))

            time.sleep(1)

            if(item['thumbnail'] != None):
                print(item['thumbnail']['alt_text'])          

    pprint.pprint(art)


if __name__ == "__main__":
    main(sys.argv)