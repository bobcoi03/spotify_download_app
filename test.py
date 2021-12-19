from spotdl.download import DownloadManager
from spotdl.parsers import parse_query
from spotdl.search import SpotifyClient, SongObject
import os

# Initialize spotify client id & secret is provided by spotdl
SpotifyClient.init(
    client_id="5f573c9620494bae87890c0f08a60293",
    client_secret="212476d9b0f3472eaa762d90b19b0ba8",
    user_auth=False,
)


spotdl_opts = {
    "query": ['https://open.spotify.com/track/58Mh6zmqSo9IvysPAXnG0h?si=3048d035855840da'],
    "output_format": "mp3",
    "download_threads": 1,
    "use_youtube": False,
    "generate_m3u": False,
    "search_threads": 2,
    "path_template": None
}

song_list = parse_query(
        spotdl_opts["query"],
        spotdl_opts["output_format"],
        spotdl_opts["download_threads"],
        spotdl_opts["use_youtube"],
        spotdl_opts["generate_m3u"],
        spotdl_opts["search_threads"],
        spotdl_opts["path_template"]
    )


print(type(song_list[0].lyrics))

DownloadManager(spotdl_opts).download_multiple_songs(song_list)

'''
with DownloadManager(spotdl_opts) as downloader:
    # Get songs
    song_list = parse_query(
        spotdl_opts["query"],
        spotdl_opts["output_format"],
        spotdl_opts["download_threads"],
        spotdl_opts["use_youtube"],
        spotdl_opts["generate_m3u"],
        spotdl_opts["search_threads"],
        spotdl_opts["path_template"]
    )

    print(song_list[0])

    # Start downloading
    if len(song_list) > 0:
        downloader.download_multiple_songs(song_list)
'''

''' 
    I need to find the Image file of each mp3, filename, artist name, album.

    I need to create a SongObject and pass it into DownloadManager.download_single_song(SongObject)
    Then I can access attributes in SongObject
'''