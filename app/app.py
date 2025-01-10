from flask import Flask, render_template, request, url_for, redirect, Response, stream_with_context, jsonify
import json
import time
import os
import re
import config
from mkvEditor import get_mkv_tracks, apply_track_changes, get_mkv_bad_default
from progress_stream import progress_listener, listener_event
from classes import Track

app = Flask(__name__)

# Function to get directory contents
def get_directory_structure(directory):
    try:
        items = os.listdir(directory)
        return {
            "directories": [item for item in items if os.path.isdir(os.path.join(directory, item))],
            "files": [
                {"name": item, "is_mkv": item.endswith(".mkv")}
                for item in items if os.path.isfile(os.path.join(directory, item))
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template("base.html")

# GET route showing all movie files
@app.route("/movies/")
def movies():
    root_dir = request.args.get('path', config.MOVIE_DIR)
    parent_dir = re.sub('/[^/]+$', '', root_dir)
    directory_structure = get_directory_structure(root_dir)
    return render_template("explorer.html", parent_path=parent_dir, current_path=root_dir, structure=directory_structure)

# GET route showing all TV show files
@app.route("/tv-shows/")
def tv_shows():
    root_dir = request.args.get('path', config.TV_SHOW_DIR)
    parent_dir = re.sub('/[^/]+$', '', root_dir)
    directory_structure = get_directory_structure(root_dir)
    return render_template("explorer.html", parent_path=parent_dir, current_path=root_dir, structure=directory_structure)

# GET route showing track details for a specific media file
@app.route("/files/")
def files():
    file_dir = request.args.get('path')
    tracks = get_mkv_tracks(file_dir)
    
    # Group tracks by track_type
    grouped_tracks = {}
    for track in tracks:
        if track.track_type:
            if track.track_type not in grouped_tracks:
                grouped_tracks[track.track_type] = []
            grouped_tracks[track.track_type].append(track)
    return render_template("file.html", file_name=file_dir.split('/')[-1], file_path=file_dir, grouped_tracks=grouped_tracks)

# GET route for showing all media files with incorrect track defaults
@app.route("/find-incorrect-defaults/")
def find_incorrect_defaults():
    default_languages = read_from_file("languages")
    return render_template("find-incorrect-defaults.html", default_languages=default_languages)

# POST route used to make changes to file tracks
@app.route('/apply_file_changes', methods=['POST'])
def apply_file_changes():
    file_path = request.args.get('file_path')
    changes = []
    for key in request.form:
        if key.startswith('track_'):
            changes.append(Track(key.split('_')[1]))
            changes[-1].default = request.form[key]
    
    apply_track_changes(file_path, changes)
    return redirect(request.referrer)

# POST route used to get info of all media that doesn't match given track requirements
@app.route("/process-incorrect-defaults/", methods=["POST"])
def process_incorrect_defaults():
    languages = request.json.get("languages")
    write_to_file("languages", languages)

    mkv_files = get_mkv_bad_default(languages)
    mkv_files_dict = []

    for mkv_file in mkv_files:
        file_dict = mkv_file.to_dict()
        for track in file_dict["tracks"]:
            track["html"] = render_template('track.html', track=track)  
        mkv_files_dict.append(file_dict)

    return jsonify(mkv_files_dict)

# Used by base.html template to stream progress of backend processes
@app.route("/stream-progress/")
def stream_progress():
    def generate():
        if progress_listener:
            yield f"data: {json.dumps(progress_listener)}\n\n"
        while True:
            listener_event.wait()
            if progress_listener:
                yield f"data: {json.dumps(progress_listener)}\n\n"
            listener_event.clear()
    return Response(stream_with_context(generate()), content_type='text/event-stream')


def write_to_file(key, data):
    file_path = os.path.join(config.CACHE_DIR, "data.json")
    
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        existing_data[key] = data

        with open(file_path, "w") as f:
            json.dump(existing_data, f, indent=4)

    except Exception as e:
        app.logger.error(f"Failed to update languages in file: {e}")

def read_from_file(key):
    file_path = os.path.join(config.CACHE_DIR, "data.json")
    
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        return existing_data.get(key)

    except Exception as e:
        app.logger.error(f"Failed to read data from file: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True)