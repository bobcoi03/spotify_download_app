''' 
    USER TYPES IN SPOTIFY LINK
    AND SITE DOWNLOADS FILES TO SERVER, 
    THEN SENDS THAT FILE TO USER AND THEN
    DELETES FILES ON THE SERVER, NO STORAGE REQUIRED.
'''
from flask import Flask, render_template, request, send_from_directory, session
from flask_session import Session
from flask.helpers import url_for
from spotdl.download import DownloadManager
from spotdl.parsers import parse_query
from spotdl.search import SpotifyClient, SongObject, from_spotify_url
import os
import shutil
import asyncio
from werkzeug.utils import redirect
import time
from spotdl.providers import metadata_provider
from spotdl.utils.song_name_utils import format_name

# Initialize spotify client id & secret is provided by spotdl
SpotifyClient.init(
    client_id="5f573c9620494bae87890c0f08a60293",
    client_secret="212476d9b0f3472eaa762d90b19b0ba8",
    user_auth=False,
)

DIRNAME = os.path.dirname(__file__)

app = Flask(__name__)
app.secret_key = 'super secret key lmao'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route("/download", methods = ['GET','POST'])
def download_page(): # str: download_link = spotify link to track
    """
    This route displays a information about a single track 
    with a download button for user to download song
    """
    if request.args.get('download_link', None) != None:
        session['download_link'] = request.args.get('download_link', None)

    # When user submits search form redirect to /download
    if request.form.get('search'):
        if request.method == 'POST':
            # if user input is a spotify url
            if "//open.spotify.com/track/" in request.form.get('search'):
                session['download_link'] = request.form.get('search')
            elif "//open.spotify.com/playlist/" in request.form.get('search'):
                """
                This should return a download page for the playlist
                """
                session['download_link'] = request.form.get('search')
        
                return redirect(url_for('download_playlist_page', download_link = request.form.get('search')))
            # If user input is a search query
            else:
                return redirect(url_for('search_page', search_query = request.form.get('search')))

    spotdl_opts = {
            "query": [session['download_link']],      # str: spotify url of track
            "output_format": "mp3",             # str: audio format
            "download_threads": 1,              
            "use_youtube": False,
            "generate_m3u": False,
            "search_threads": 2,                
            "path_template": None               # None don't know what this is
        }

    # Query info using spotify api --> returns list of SongObjects or list[SongObject,...,SongObject]
    song_list = parse_query(
            spotdl_opts["query"],
            spotdl_opts["output_format"],
            spotdl_opts["download_threads"],
            spotdl_opts["use_youtube"],
            spotdl_opts["generate_m3u"],
            spotdl_opts["search_threads"],
            spotdl_opts["path_template"]
        )
    # song object for easier use in Javascript. check spotdl.search.SongObject to find methods and attributes.
    songObj = {
            'song_name': song_list[0].song_name,
            'album_cover_url': song_list[0].album_cover_url,            # str: url of img to cover album
            'file_name': ", ".join(song_list[0].contributing_artists) + " - " + song_list[0].song_name + '.mp3',
            'list_of_artist_names': song_list[0].contributing_artists,  # str array: of contributing artists to track
            'album': song_list[0].album_name,                           # str: album name
            'duration': song_list[0].duration,                          # float: in seconds duraion of song
            'youtube_link': song_list[0].youtube_link                   # str:
        }

    print(f'songObj["file_name"]: {songObj["file_name"]}')

    # Handle Download
    if request.form.get('download_button') == 'Download':
        # Have to get download link again using AJAX for some reason
            # This downloads the song to current directory

        #   If file already in uploads folder 
        #      --> send user files in uploads folder
        #   Else
        #      --> Download song and move it into uploads folder
        if os.path.isfile(f'./{songObj["file_name"]}'):
            pass
        else:
            DownloadManager(spotdl_opts).download_multiple_songs(song_list)
            #shutil.move(songObj["file_name"], './uploads/')
        
        print(f'Downloaded completed: {songObj["file_name"]}')

        return send_from_directory('./', songObj["file_name"], as_attachment=True)

    return render_template('download.html', download_link=session['download_link'], songObj = songObj)

@app.route("/", methods = ['GET','POST'])
def main():
    # When user submits search form redirect to /download or /search
    if request.form.get('search'):
        if request.method == 'POST':
            search_input = request.form.get('search')
            # if user input is a spotify url
            if "//open.spotify.com/track/" in search_input:
                return redirect(url_for('download_page', download_link = search_input))
            elif "//open.spotify.com/playlist/" in search_input:
                return redirect(url_for('download_playlist_page', download_link = search_input)) 
            # If user input is a search query
            else:
                return redirect(url_for('search_page', search_query = search_input))

    return render_template('main.html')

@app.route('/search', methods = ['GET', 'POST'])
def search_page():
    # When user submits search form redirect to /download or /search
    if request.form.get('search'):
        if request.method == 'POST':
            search_input = request.form.get('search')
            # if user input is a spotify url
            if "//open.spotify.com/track/" in search_input:
                return redirect(url_for('download_page', download_link = search_input))
            elif "//open.spotify.com/playlist/" in search_input:
                return redirect(url_for('download_playlist_page', download_link = search_input)) 
            # If user input is a search query
            else:
                return redirect(url_for('search_page', search_query = search_input))

    if request.args.get('search_query', None) != None:
        session['search_query'] = request.args.get('search_query')

    # list[SongObject,...,SongObject]
    start_time = time.time()
    results_of_search_query = search_query(session['search_query'])
    end_time = time.time()
    time_lapsed = end_time - start_time
    print(f'Total search time {time_convert(time_lapsed)}')

    # turn results_of_search_query into JSON
    results_of_search_query_json = {}
    for i in range(len(results_of_search_query)):
        # Filename doesn't include .mp3
        results_of_search_query_json[results_of_search_query[i].file_name] = {
            'song_name': results_of_search_query[i].song_name,
            'album_cover_url': results_of_search_query[i].album_cover_url,
            'list_of_artists_names': results_of_search_query[i].contributing_artists,
            'duration':results_of_search_query[i].duration,
            'spotify_link':results_of_search_query[i].spotify_url}

    return render_template('search_page.html', results_of_search_query=results_of_search_query_json)

@app.route('/download/playlist', methods = ['GET','POST'])
def download_playlist_page():
    ''''
    IF USER INPUT TO SEARCH HAS "//open.spotify.com/playlist/" in it
    '''
    if request.args.get('download_link', None) != None:
        session['download_link'] = request.args.get('download_link')

    # When user submits search form redirect to /download or /search
    if request.form.get('search'):
        if request.method == 'POST':
            search_input = request.form.get('search')
            # if user input is a spotify url
            if "//open.spotify.com/track/" in search_input:
                return redirect(url_for('download_page', download_link = search_input))
            elif "//open.spotify.com/playlist/" in search_input:
                return redirect(url_for('download_playlist_page', download_link = search_input)) 
            # If user input is a search query
            else:
                return redirect(url_for('search_page', search_query = search_input))

    playlist_url = session['download_link']


    return render_template('download_playlist.html')

@app.route("/terms_of_service")
def terms_of_service_page():
    return render_template('terms_of_service.html')

def search_query(query: str):
    """
    THIS FUNCTION TAKES search query AS INPUT AND RETURN
    a `list<SongObject>`.
    """
    
    songs = [] # This list contains searchSongObject for each song
    list_song_urls = []
    # get a spotify client
    spotify_client = SpotifyClient()

    # Use spotify search
    search_results = spotify_client.search(query, type="track")

    number_of_search_results = len(search_results.get("tracks", {}).get("items", []))

    # return first result link or if no matches are found, raise Exception
    if search_results is None or number_of_search_results == 0:
        raise Exception("No song matches found on Spotify")

    # Adds each song url to list_song_urls
    for i in range(0, number_of_search_results):
        # Get the Song Metadata
        song_url = "http://open.spotify.com/track/" + search_results["tracks"]["items"][i]["id"]
        raw_track_meta, raw_artist_meta, raw_album_meta = metadata_provider.from_url(song_url)

        # for searchSongObject
        song_name = search_results["tracks"]["items"][i]["name"]
        cover_url = search_results["tracks"]["items"][i]["album"]["images"][0]["url"]
        contributing_artists = [artist["name"] for artist in raw_track_meta["artists"]]   
        duration = search_results["tracks"]["items"][i]["duration_ms"] / 1000 # convert to seconds

        list_song_urls.append(song_url)
        # create SongObject and append to songs[]
        song = searchSongObject(song_url, contributing_artists, song_name, duration, cover_url)
        songs.append(song)

    return songs

# This is to display in /search because creating SongObject would mean you have to use youtube API, which takes too long
class searchSongObject:
    def __init__(self,
        spotify_url: str,
        contributing_artists: list,
        song_name: str,
        duration: float, 
        album_cover_url: str) -> None:

        self._spotify_url = spotify_url
        self._contributing_artists = contributing_artists
        self._song_name = song_name
        self._duration = duration
        self._album_cover_url = album_cover_url
    
    @property
    def spotify_url(self):
        return self._spotify_url
    
    @property
    def contributing_artists(self):
        return self._contributing_artists
    
    @property
    def song_name(self):
        return self._song_name
    
    @property
    def duration(self):
        return self._duration
    
    @property
    def album_cover_url(self):
        return self._album_cover_url

    @property
    def file_name(self):
        return self.create_file_name(self._song_name, self._contributing_artists)

    @staticmethod
    def create_file_name(song_name: str, song_artists: list[str]) -> str:
        # build file name of converted file
        # the main artist is always included
        artist_string = song_artists[0]

        # ! we eliminate contributing artist names that are also in the song name, else we
        # ! would end up with things like 'Jetta, Mastubs - I'd love to change the world
        # ! (Mastubs REMIX).mp3' which is kinda an odd file name.
        for artist in song_artists[1:]:
            if artist.lower() not in song_name.lower():
                artist_string += ", " + artist

        converted_file_name = artist_string + " - " + song_name

        return format_name(converted_file_name)


def time_convert(sec):
  mins = sec // 60
  sec = sec % 60
  hours = mins // 60
  mins = mins % 60
  return "{0}:{1}:{2}".format(int(hours),int(mins),sec)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)
