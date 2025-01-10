import hashlib
import config
import os
import json
from classes import MkvFile

cached_mkv_files = None
cached_mkv_hashes = {}

def calculate_directory_hash(directory):
    hash_obj = hashlib.md5()
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                hash_obj.update(name.encode())  # Add filename to hash
                hash_obj.update(str(os.path.getmtime(file_path)).encode())  # Add file mtime to hash
            except FileNotFoundError:
                continue  # Skip files that are deleted during the operation
    return hash_obj.hexdigest()

def is_cache_valid():
    cached_mkv_hashes = read_from_cache("cached_mkv_hashes") or {}

    for directory in config.SEARCH_DIRS:
        current_hash = calculate_directory_hash(directory)
        if directory not in cached_mkv_hashes or cached_mkv_hashes[directory] != current_hash:
            cached_mkv_hashes[directory] = current_hash
            return False
    return True

def update_cache(mkv_files):
    cached_mkv_files = mkv_files

    for directory in config.SEARCH_DIRS:
        cached_mkv_hashes[directory] = calculate_directory_hash(directory)

    write_to_cache("cached_mkv_files", [mkv_file.to_dict() for mkv_file in cached_mkv_files])
    write_to_cache("cached_mkv_hashes", cached_mkv_hashes)

def get_cached_mkv_files():
    cached_mkv_files = [MkvFile.from_dict(item) for item in read_from_cache("cached_mkv_files")]
    cached_mkv_hashes = read_from_cache("cached_mkv_hashes") or {}

    if cached_mkv_files is not None and is_cache_valid():
        print("Using cached MKV files.")
        return cached_mkv_files
    
    return None

def write_to_cache(key, data):
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
        print(f"Failed to update languages in file: {e}")

def read_from_cache(key):
    file_path = os.path.join(config.CACHE_DIR, "data.json")
    
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        return existing_data.get(key)

    except Exception as e:
        print(f"Failed to read data from file: {e}")
        return None