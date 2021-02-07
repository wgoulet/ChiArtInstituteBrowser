# ChiArtInstituteBrowser
Collection of scripts for interfacing with Chicago Art Institute APIs

- main.py - Basic Python script that searches for artists by name and retrieves any published images for the artist that are available. Note that requests are throttled by 1 second per request per the guidelines published on http://api.artic.edu/docs/#introduction. Images are saved with the artist name and artwork title as fullsize JPEGs. 
