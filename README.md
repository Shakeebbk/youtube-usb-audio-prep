Make a copy of config.json.sample as config.json and fill the relevant fields.

To get playlist items from youtube:
`go run music.go`

To download mp3 of relevant items from playlist
`./music_dir_sync.py`

To copy randomly picked songs from the downloaded items into an usb with given size in GBs
`sudo ./music_usb_sync.py 1 /tmp/usb/`

### Get youtbe API key
https://developers.google.com/youtube/registering_an_application

### Dependencies
```
golang - go1.13.8

go get google.golang.org/api/youtube/v3

pip3 install -U youtube_dl

sudo apt install ffmpeg
```
