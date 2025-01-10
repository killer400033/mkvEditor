import subprocess
import sys
import re
import os
import config
from concurrent.futures import ThreadPoolExecutor
import time
from threading import Condition
from mkvFileCache import get_cached_mkv_files, update_cache
from classes import Track, MkvFile
from progress_stream import progress_message, progress_error

# Global variables
process_condition = Condition()
is_processing = False

def get_mkv_tracks(mkv_file):
    progress_message(f"Getting tracks from {mkv_file}")
    try:
        # Get track information using mkvinfo
        cmd = [config.MKVINFO, mkv_file]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while reading MKV file: {e}")
        print(e.output)
        progress_error(f"Error occurred while reading MKV file: {e}")
        return None

    tracks = []
    track_lines = result.stdout.splitlines()

    for line in track_lines:
        match_track_number = re.match(r"\|\s*\+ Track number: (\d+)", line)

        # Append new track
        if match_track_number:
            tracks.append(Track(match_track_number.group(1)))
            tracks[-1].file_name = mkv_file.split('/')[-1]
            continue

        # Get track type
        if "Track type:" in line:
            tracks[-1].track_type = line.split(":")[1].strip()

        # Get track language
        if "Language:" in line:
            tracks[-1].language = line.split(":")[1].strip()
        
        if "\"Default track\" flag:" in line:
            tracks[-1].default = line.split(":")[1].strip()

    progress_message(f"Done getting tracks from {mkv_file}")
    return tracks

def apply_track_changes(mkv_file, tracks):
    progress_message(f"Applying changes to {mkv_file}")
    cmd = [config.MKVPROPEDIT, mkv_file]
    for track in tracks:
        cmd += ["--edit", f"track:{track.track_id}", "--set", F"flag-default={track.default}"]
    
    # Run command
    try:
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        progress_message(f"Done applying changes to {mkv_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while editing MKV file: {e}")
        print(e.output)
        progress_error(f"Error occurred while editing MKV file: {e}")


def reset_default_tracks(mkv_file, correct_matches):
    progress_message(f"Resetting default tracks in {mkv_file}")
    if not mkv_file.endswith(".mkv"):
        print("Error: The provided file is not an MKV file.")
        return

    tracks = get_mkv_tracks(mkv_file)
    if tracks is None:
        return
    
    # Build command
    cmd = [config.MKVPROPEDIT, mkv_file]
    for track in tracks:
        if track.track_type.lower() in ['audio', 'subtitles']:
            cmd += ["--edit", f"track:{track.track_id}", "--set", F"flag-default=0"]
    
    # Run command
    try:
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
        progress_message(f"Done resetting default tracks in {mkv_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while editing MKV file: {e}")
        print(e.output)
        progress_error(f"Error occurred while editing MKV file: {e}")

def process_mkv_file(mkv_file):
    mkv = MkvFile(mkv_file)
    mkv.tracks = get_mkv_tracks(mkv_file)
    return mkv if mkv.tracks is not None else None

def get_all_mkv_files():
    global is_processing
    progress_message("Reading all mkv files...")
    with process_condition:
        while is_processing:
            print("Waiting for the current process to complete...")
            process_condition.wait()
    
    # Check if cached is valid
    if get_cached_mkv_files(): return get_cached_mkv_files()

    mkv_files = []
    is_processing = True
    with ThreadPoolExecutor() as executor:
        futures = []

        # Get all files
        for mkv_path in config.SEARCH_DIRS:
            for root, dirs, files in os.walk(mkv_path):
                for filename in files:
                    mkv_file = os.path.join(root, filename)

                    if os.path.isfile(mkv_file) and mkv_file.endswith(".mkv"):
                        futures.append(executor.submit(process_mkv_file, mkv_file))

        for future in futures:
            result = future.result()
            if result:
                mkv_files.append(result)

    update_cache(mkv_files)

    with process_condition:
        is_processing = False
        process_condition.notify_all()
    progress_message("Done")

    return mkv_files

def get_mkv_bad_default(languages):
    mkv_files = get_all_mkv_files()
    if mkv_files is None:
        return None

    progress_message(f"Filtering files...")

    # Filter for all "bad" files
    files_with_bad_default = []
    for file in mkv_files:
        invalid_tracks = [
            track for track in file.tracks
            if (track.track_type in ['audio', 'subtitles'] and
                track.default == '1') and
                ((track.language is None and "null" not in [lang.lower() for lang in languages]) or
                (track.language is not None and track.language.lower() not in [lang.lower() for lang in languages]))
        ]
        if invalid_tracks:
            files_with_bad_default.append(file)

    progress_message("Done")
    return files_with_bad_default