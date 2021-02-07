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
    searchqry = { 
        "query": { 
            "bool": { 
                "must": {"term": {"agent_type_id": 7}}, 
            "filter": { "match": {"title":"hopper"}}} 
        } 
    } 
    #searchqry = { 
    #    "query":  
    #        {"term": {"title":"hopper"}}
    #} 
    jsearchqry = json.dumps(searchqry)
    codedqry = urllib.parse.urlencode(searchqry)
    pprint.pprint(codedqry)
    url = "https://api.artic.edu/api/v1/agents/search?limit=100"
    #url = "https://api.artic.edu/api/v1/agents/search?params={0}&limit=100".format(codedqry)
    #url = "https://www.artic.edu/collection/categorySearch/artists?q=hopper&categoryQuery=ho"
    r = requests.post(url,headers=headers,json=searchqry)
    r.raise_for_status()
    agents = r.json()
    pprint.pprint(agents)
    with open('artists.csv','w') as csvfile:
        fieldnames = ["_score","api_model","api_link","id","title","timestamp"]
        writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
        writer.writeheader()
        url = "https://api.artic.edu/api/v1/agents/search?params={0}&limit=0".format(codedqry)
        r = requests.get(url,headers=headers)
        r.raise_for_status()
        agents = r.json()
        resultsize = agents['pagination']['total']
        pages = int(resultsize / 100)
        for i in range(1,pages):
            url = "https://api.artic.edu/api/v1/agents/search?params={0}&limit=100&page={1}".format(codedqry,i)
            r = requests.get(url,headers=headers)
            r.raise_for_status()
            agents = r.json()
            for a in agents['data']:
                writer.writerow(a)
            time.sleep(1)

    return
    url = "https://api.artic.edu/api/v1/artworks/search?q=hopper&limit=0"

    r = requests.get(url,headers=headers)
    r.raise_for_status()
    art = r.json()
    resultsize = art['pagination']['total']
    pages = int(resultsize / 10)
    
    for i in range(1,pages):
        url = "https://api.artic.edu/api/v1/artworks/search?q=hopper&limit=10&page={0}".format(i)
        r = requests.get(url,headers=headers)
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
                file = open("{0}.jpg".format(item['title']),"wb")
                file.write(img)
            except:
                print("Unable to get image for {0}".format(item['title']))

            time.sleep(1)

            if(item['thumbnail'] != None):
                print(item['thumbnail']['alt_text'])          

    pprint.pprint(art)


if __name__ == "__main__":
    main()