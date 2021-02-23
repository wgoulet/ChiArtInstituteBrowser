import argparse
import csv
import json
import math
import os
import pickle
import pprint
import re
import sqlite3
import subprocess
import sys
import time
import urllib.parse
from io import FileIO
from pathlib import Path
from typing import Optional
import ffmpeg
import mutagen
import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
import uvicorn
from fastapi.responses import StreamingResponse
import io

class Artwork():
    title: str
    arttype: str
    artist: str
    image: Optional[str] = None
    video: Optional[bytes] = None

def main(argv):
    print("hello world")
 
    connection = sqlite3.connect("artinstvid.db",detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    cursor = connection.cursor()

    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='artwork'")

    if cursor.fetchone()[0]!=1:
        print("Creating table")
        cursor.execute("CREATE TABLE artwork (title TEXT, arttype TEXT, \
            artist TEXT, image BLOB, video BLOB)")
        connection.commit()
    item = Artwork()
    with open("Edward Hopper-Nighthawks.jpg","rb") as imgfile:
        item.image = imgfile.read()
    with open("edward hopper-Nighthawks-all.mp4","rb") as vidfile:
        item.video = vidfile.read()
    cursor = connection.cursor()
    item.artist = "Edward Hopper"
    item.title = "Nighthawks"
    item.arttype = "Painting"
    record = (item.artist,item.title,item.arttype,item.image,item.video)
    cursor.execute("INSERT INTO artwork (artist, title, arttype, image, video) VALUES (?,?,?,?,?)",record)
    connection.commit()

    cursor.execute("SELECT image from artwork")
    timage = cursor.fetchone()[0]
    with open("test.jpg","wb") as testimg:
        testimg.write(timage)
    cursor.execute("SELECT video from artwork")
    tvideo = cursor.fetchone()[0]
    with open("test.mp4","wb") as testvid:
        testvid.write(tvideo)

    app = FastAPI()

    origins = [
    "http://localhost",
    "http://localhost:3000",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.route("/list")
    def read_root(request):
        return JSONResponse({"you are": "authenticated"})


    @app.route("/vidtest")
    def read_vid(request):
        connection = sqlite3.connect("artinstvid.db",detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        cursor.execute("SELECT video from artwork")
        tvideo = cursor.fetchone()[0]
        connection.close()
        #tvideo = open("test.mp4","rb")
        size = len(tvideo)
        # Let the client know we support content ranges
        if 'Range' not in request.headers:
            headers = {
                "Accept-Ranges": "bytes"
            }
            return Response(content=None, media_type="video/mp4",status_code=206,headers=headers)
        # From https://dev.to/singhpratyush/the-taste-of-media-streaming-with-flask-58a4
        m = re.search('(\d+)-(\d*)', request.headers['range'])
        g = m.groups()
        byte1, byte2 = 0, None
        if g[0]:
            byte1 = int(g[0])
        if g[1]:
            byte2 = int(g[1])
        length = size - byte1
        if byte2:
            length = byte2 + 1 - byte1
        stream = io.BytesIO(tvideo[byte1: byte2])
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Length": F"{len(tvideo)}",
            #"Content-Range": F"bytes {asked}-{sz-1}/{sz}",
            "Content-Range" : F"bytes {byte1}-{byte1 + length - 1}/{size}"
        }
        #response =  StreamingResponse(streaming_file(file_path, CS, asked), headers=headers,
        return StreamingResponse(stream, media_type="video/mp4",status_code=206,headers=headers)

    @app.route("/imgtest")
    def read_img(request):
        connection = sqlite3.connect("artinstvid.db",detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        cursor.execute("SELECT image from artwork")
        tvideo = cursor.fetchone()[0]
        connection.close()
        stream = io.BytesIO(tvideo)
        #tvideo = open("test.mp4","rb")
        return StreamingResponse(stream, media_type="image/jpeg")

    uvicorn.run(app, host='127.0.0.1', port=8000)

if __name__ == "__main__":
	main(sys.argv)
