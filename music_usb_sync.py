#!/usr/bin/env python3

import os
import sys
import random
import json

with open('config.json') as f:
    raw_config = f.read()

config = json.loads(raw_config)
# intentionally not handling key errors, let it fail here
MUSIC_DEST = config["MUSIC_DEST"]

def run():
    import glob
    files = glob.glob(f'{MUSIC_DEST}/**/*.mp3', recursive=True)
    print(len(files))

    size = 0
    req_size = int(sys.argv[1]) * 1024 * 1024 * 1024
    to_copy = []

    while files and size < req_size:
        choice = random.choice(files)
        files.remove(choice)
        size += os.stat(choice).st_size
        to_copy.append(choice)

    #print(to_copy)
    with open('/tmp/to_copy.txt', 'w') as f:
        f.writelines([fn+'\n' for fn in to_copy])

    dst = sys.argv[2]
    cmd = f'rsync -zv --progress --no-relative --files-from=/tmp/to_copy.txt / {dst}'
    #print(cmd)
    os.system(cmd)

run()
