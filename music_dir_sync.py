#!/usr/bin/env python3

import json
import os
import time

with open('config.json') as f:
    raw_config = f.read()

config = json.loads(raw_config)
# intentionally not handling key errors, let it fail here
STORE_FILE = config["STORE_PATH"]
MUSIC_DEST = config["MUSIC_DEST"]

def get_titles(store):
    titles = {}
    for playlist, list in store.items():
        titles[playlist] = []
        for title, id in list.items():
            titles[playlist].append(title)
    return titles

def get_ids(store):
    ids = {}
    for playlist, list in store.items():
        ids[playlist] = []
        for title, id in list.items():
            ids[playlist].append(id)
    return ids

def get_dir_titles(music_root):
    titles = {}
    _, folders, _ = next(os.walk(music_root))
    for folder in folders:
        titles[folder] = []
        _, _, files = next(os.walk(f'{music_root}/{folder}'))
        titles[folder] = [f.replace('.mp3', '').replace('_', '|') for f in files]
    return titles

def get_missing(src, dst):
    missing = {}
    for folder, files in src.items():
        missing[folder] = []
        if folder not in dst:
            continue
        import difflib
        def check_in(ele, li):
            for e in li:
                if difflib.SequenceMatcher(None, e, ele).ratio() > 0.6:
                    return True
            return False
        missing[folder] = [f for f in files if not check_in(f, dst[folder])]
    return missing

def download_mp3(folder, id):
    cmd = f'youtube-dl -i --extract-audio --audio-format mp3 --audio-quality 0 -o \'{MUSIC_DEST}/{folder}/%(title)s.%(ext)s\' \'https://www.youtube.com/watch?v={id}\''
    #print(cmd)
    os.system(cmd)

def run():
    store = None
    with open(STORE_FILE) as f:
        store = f.read()
    
    store = json.loads(store)

    titles = get_titles(store)
    existing_titles = get_dir_titles(MUSIC_DEST)

    missing = get_missing(existing_titles, titles)
    print(f'To Delete: {missing}')

    missing = get_missing(titles, existing_titles)
    print(f'To Download: {missing}')

    for folder, songs in missing.items():
        os.system(f'mkdir \'{MUSIC_DEST}/{folder}\'')
        os.system('sync')
        time.sleep(2)
        for song in songs:
            download_mp3(folder, store[folder][song])


if __name__ == "__main__":
    run()

