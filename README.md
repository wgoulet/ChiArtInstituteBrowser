# ChiArtInstituteBrowser
Collection of scripts for interfacing with Chicago Art Institute APIs

- main.py - Basic Python script that searches for artists by name and retrieves any published images (and if available any audio tour video) for the artist that are available. The script then uses ffmpeg to craft videos from still images of the artwork using the audio tour media as a soundtrack. Note that requests are throttled by 1 second per request per the guidelines published on http://api.artic.edu/docs/#introduction. Images are saved with the artist name and artwork title as fullsize JPEGs. NOTE: In order to run the script, the ffmpeg utility must be installed on your system and available on your $PATH.

- findallaudio.py - Python script that performs same core task as main.py, except it queries for all audio tour stop recordings that are available then fetches associated artwork & artist info to create videos of the images + audio tour recordings.

- videodb.py - Python script that creates a database containing generated files and serves the content as a webservice. Uses the FastAPI library to stream video content using HTTP partial content (required for the videos to play correctly in Safari.)
