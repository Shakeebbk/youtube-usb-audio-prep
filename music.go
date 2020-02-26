package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"strings"

	"google.golang.org/api/option"

	"google.golang.org/api/youtube/v3"
)

func main() {
	config := make(map[string]string)
	rawConfig, err := ioutil.ReadFile("config.json")
	if err != nil {
		fmt.Println("Error reading config.json")
		fmt.Println(err)
		return
	}
	err = json.Unmarshal(rawConfig, &config)
	if err != nil {
		fmt.Println("Error parsing config.json")
		fmt.Println(err)
		return
	}

	API_KEY := config["API_KEY"]
	CHANNEL_ID := config["CHANNEL_ID"]
	STORE_PATH := fmt.Sprintf("%v/music.store", config["MUSIC_DEST"])

	ctx := context.Background()
	youtubeService, err := youtube.NewService(ctx, option.WithAPIKey(API_KEY))

	plService := youtube.NewPlaylistsService(youtubeService)

	pl := plService.List("snippet")
	pl = pl.ChannelId(CHANNEL_ID)
	// response := playlistsList(youtubeService, "snippet,contentDetails", *channelId, *hl, *maxResults, *mine, *onBehalfOfContentOwner, *pageToken, *playlistId)
	response, err := pl.Do()
	if err != nil {
		fmt.Println("Error getting playlists")
		fmt.Println(err)
		return
	}

	store := make(map[string]map[string]string)
	for _, playlist := range response.Items {
		playlistId := playlist.Id
		playlistTitle := playlist.Snippet.Title

		// Print the playlist ID and title for the playlist resource.
		if strings.HasPrefix(playlistTitle, "music_") {
			// fmt.Println(playlistId, ": ", playlistTitle)
			store[playlistTitle] = make(map[string]string)

			plItemService := youtube.NewPlaylistItemsService(youtubeService)
			plItems := plItemService.List("snippet")
			plItems = plItems.PlaylistId(playlistId)
			plItems = plItems.MaxResults(50)

			itemsResp, err := plItems.Do()
			if err != nil {
				fmt.Println("Error getting playlist items")
				fmt.Println(err)
				return
			}

			totalResults := int(itemsResp.PageInfo.TotalResults)
			pageResults := len(itemsResp.Items)
			fmt.Printf("Playlist: %v TotalResults: %v, Per Page: %v\n", playlistTitle, totalResults, pageResults)
			numPages := int(totalResults / pageResults)
			if (totalResults % pageResults) > 0 {
				numPages += 1
			}
			for numPages > 0 {
				fmt.Printf("Page: %v\n", numPages)
				for _, item := range itemsResp.Items {
					// fmt.Println(item.Snippet.Title)
					store[playlistTitle][item.Snippet.ResourceId.VideoId] = item.Snippet.Title
				}
				numPages -= 1
				plItems.PageToken(itemsResp.NextPageToken)
				itemsResp, err = plItems.Do()
				if err != nil {
					fmt.Println("Error getting playlist pages")
					fmt.Println(err)
					return
				}
			}
		}
	}
	jsonStore, _ := json.MarshalIndent(store, "", "  ")
	file, err := os.Create(STORE_PATH)
	file.Write(jsonStore)
	defer file.Close()
}
