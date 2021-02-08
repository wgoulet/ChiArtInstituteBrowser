import os
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

def main():
    print ("hello world")
    headers = {'user-agent': 'art-institute-browse/wgoulet@gmail.com'}

    # search only for individual artists
    artist = "van gogh"
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
                    audfclip = moviepy.editor.AudioFileClip(audfname,fps= 44100)
                    audfclip.close()
                    audinfo = mutagen.File(audfname)
                    audlen = audinfo.info.length


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
                file = open("{0}-{1}.jpg".format(artist,item['title']),"wb")
                file.write(img)
                file.close()
                clip = moviepy.editor.ImageClip("{0}-{1}.jpg".format(artist,item['title']),"rb")
                clip.duration = int(math.ceil(audlen))
                vclip = clip.set_duration(int(math.ceil(audlen)))
                audio = moviepy.editor.AudioFileClip(audfname)
                final = vclip.set_audio(audio)
                final.write_videofile("{0}-{1}.mp4".format(artist,item['title']),
                    codec= 'mpeg4',fps=30,audio=True)
            except:
                print("Unable to get image for {0}".format(item['title']))
                raise

            time.sleep(1)

            if(item['thumbnail'] != None):
                print(item['thumbnail']['alt_text'])          

    pprint.pprint(art)


if __name__ == "__main__":
    main()