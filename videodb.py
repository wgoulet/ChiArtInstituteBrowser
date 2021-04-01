import argparse
import csv
import json
import math
import os
import pickle
import pprint
import re
import subprocess
import sys
import time
import urllib.parse
from io import FileIO
from pathlib import Path
from typing import Optional
from pymongo import MongoClient
import ffmpeg
import mutagen
import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, Response
import uvicorn
from fastapi.responses import StreamingResponse
import io

class Artwork(BaseModel):
	title: str
	arttype: str
	artist: str
	image: Optional[str] = None
	video: Optional[bytes] = None

def main(argv):
	print("hello world")
 
	item = Artwork(artist="",title="",arttype="")
	with open("Edward Hopper-Nighthawks.jpg","rb") as imgfile:
		item.image = imgfile.read()
	with open("edward hopper-Nighthawks-all.mp4","rb") as vidfile:
		item.video = vidfile.read()
	item.artist = "Edward Hopper"
	item.title = "Nighthawks"
	item.arttype = "Painting"

	client = MongoClient()
	db = client.vid_database
	collection = db.vid_collection
	collection.insert_one(item.dict())

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

	@app.route("/viddetails")
	def get_viddetails(request):
		item = Artwork(artist="",title="",arttype="")
		client = MongoClient()
		db = client.vid_database
		collection = db.vid_collection
		record = collection.find_one()
		item.artist = record['artist']
		item.title = record['title']
		item.arttype = record['arttype']
		headers = {"content-Type":"application/json"}
		return JSONResponse(item.dict())

	# From https://stackoverflow.com/questions/57314357/streaming-video-files-using-flask
	def get_chunk(byte1=None, byte2=None):
		start = 0
		length = 102400

		client = MongoClient()
		db = client.vid_database
		collection = db.vid_collection
		record = collection.find_one()
		tvideo = record['video']


		file_size = len(tvideo)
		if byte1 < file_size:
			start = byte1
		if byte2:
			length = byte2 + 1 - byte1
		else:
			length = file_size - start
		stream = io.BytesIO(tvideo)
		stream.seek(start)
		chunk = stream.read(length)
		stream.close()
		return chunk, start, length, file_size


	@app.route("/vidtest")
	def read_vid(request):
		range_header = request.headers.get('Range', None)
		byte1, byte2 = 0, None
		if range_header:
			match = re.search(r'(\d+)-(\d*)', range_header)
			groups = match.groups()

			if groups[0]:
				byte1 = int(groups[0])
			if groups[1]:
				byte2 = int(groups[1])
		chunk, start, length, file_size = get_chunk(byte1, byte2)
		stream = io.BytesIO(chunk)
		headers = {'Content-Range': 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size)}
		return StreamingResponse(stream,status_code=206,headers=headers,media_type='video/mp4')

	@app.route("/imgtest")
	def read_img(request):
		client = MongoClient()
		db = client.vid_database
		collection = db.vid_collection
		record = collection.find_one()
		tvideo = record['video']
		tvideo = cursor.fetchone()[0]
		connection.close()
		stream = io.BytesIO(tvideo)
		#tvideo = open("test.mp4","rb")
		return StreamingResponse(stream, media_type="image/jpeg")

	uvicorn.run(app, host='127.0.0.1', port=8000)

if __name__ == "__main__":
	main(sys.argv)
