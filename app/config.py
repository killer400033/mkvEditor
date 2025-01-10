import os

MOVIE_DIR = os.getenv("MOVIE_DIR", "/mnt/movies")
TV_SHOW_DIR = os.getenv("TV_SHOW_DIR", "/mnt/tvshows")
CACHE_DIR = os.getenv("CACHE_DIR", "/mnt/cache")

SEARCH_DIRS = [MOVIE_DIR, TV_SHOW_DIR]
MKVPROPEDIT = "mkvpropedit"
MKVINFO = "mkvinfo"