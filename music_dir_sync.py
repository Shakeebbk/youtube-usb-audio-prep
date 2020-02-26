#!/usr/bin/env python3

import json
import os
import time
import subprocess

with open('config.json') as f:
    raw_config = f.read()

config = json.loads(raw_config)
# intentionally not handling key errors, let it fail here
MUSIC_DEST = config["MUSIC_DEST"]
STORE_FILE = f'{MUSIC_DEST}/music.store'

DIR_STORE = f'{MUSIC_DEST}/music_dir_map.store'

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

def get_ids_flat(store):
    ids = []
    for playlist, ll in store.items():
        ids += ll.keys()
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
    cmd = f'youtube-dl -i --extract-audio --audio-format mp3 --audio-quality 0 -o \'{MUSIC_DEST}/{folder}/%(title)s.%(ext)s\' \'https://www.youtube.com/watch?v={id}\' >> {MUSIC_DEST}/youtube_dl.log 2>&1'
    #print(cmd)
    os.system(cmd)
    cmd = f'ls -ltcr {MUSIC_DEST}/{folder} | grep -e \'.mp3\' | tail -1 | '+'awk \'{print substr($0, index($0,$9))}\''
    result = subprocess.run(['bash', '-c', cmd], stdout=subprocess.PIPE)
    name = result.stdout.decode('utf-8').strip('\n')
    return f'{MUSIC_DEST}/{folder}/{name}'

def run():
    store = {}
    with open(STORE_FILE) as f:
        store = f.read()

    store = json.loads(store)

    dir_store = {}
    try:
        with open(DIR_STORE) as f:
            dir_store = f.read()

        dir_store = json.loads(dir_store)
    except Exception as e:
        print(e)
        # most likely file doest exist
        pass

    store_ids = get_ids_flat(store)
    missing_on_youtube = [idx for idx in dir_store.keys() if idx not in store_ids]
    print(f'To Delete: {missing_on_youtube}')

    for idx in missing_on_youtube:
        cmd = f'rm -rf \'{dir_store[idx]}\''
        print(cmd)
        #os.system(cmd)

    missing_local = {}
    for playlist, songs in store.items():
        missing_local[playlist] = {}
        for song_id, song_name in songs.items():
            if song_id not in dir_store.keys():
                missing_local[playlist][song_id] = song_name

    print(f'To Download: {missing_local}')

    for folder, songs in missing_local.items():
        os.system(f'mkdir \'{MUSIC_DEST}/{folder}\'')
        os.system(f'echo "" > \'{MUSIC_DEST}/{folder}/youtube_dl.log\'')
        os.system('sync')
        time.sleep(2)
        for song_id, song_name in songs.items():
            download_name = download_mp3(folder, song_id)
            print(f'Downloaded: {download_name}')
            dir_store[song_id] = download_name

    with open(DIR_STORE, 'w') as f:
        f.write(json.dumps(dir_store, indent=2))


if __name__ == "__main__":
    run()

