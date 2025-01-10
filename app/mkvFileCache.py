import hashlib
import config
import os

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
    global cached_mkv_hashes

    for directory in config.SEARCH_DIRS:
        current_hash = calculate_directory_hash(directory)
        if directory not in cached_mkv_hashes or cached_mkv_hashes[directory] != current_hash:
            cached_mkv_hashes[directory] = current_hash
            return False
    return True

def update_cache(mkv_files):
    global cached_mkv_files
    cached_mkv_files = mkv_files
    for directory in config.SEARCH_DIRS:
        cached_mkv_hashes[directory] = calculate_directory_hash(directory)

def get_cached_mkv_files():
    global cached_mkv_files, cached_mkv_hashes
    if cached_mkv_files is not None and is_cache_valid():
        print("Using cached MKV files.")
        return cached_mkv_files
    
    return None