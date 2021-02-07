import os
import requests
import pprint
import time
import json
import urllib.parse
import csv

def main():
    print ("hello world")
    headers = {'user-agent': 'art-institute-browse/wgoulet@gmail.com'}

    # search only for individual artists
    artist = "paul klee"
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
    pages = int(resultsize / 10)
    
    for i in range(1,pages):
        url = "https://api.artic.edu/api/v1/artworks/search?&limit=10&page={0}".format(i)
        r = requests.post(url,headers=headers,json=searchqry)
        r.raise_for_status()
        art = r.json()
        for item in art['data']:
            print(item['title']) 
            print(item['id'])
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
            except:
                print("Unable to get image for {0}".format(item['title']))

            time.sleep(1)

            if(item['thumbnail'] != None):
                print(item['thumbnail']['alt_text'])          

    pprint.pprint(art)


if __name__ == "__main__":
    main()