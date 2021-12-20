''' 
    USER TYPES IN SPOTIFY LINK
    AND SITE DOWNLOADS FILES TO SERVER, 
    THEN SENDS THAT FILE TO USER AND THEN
    DELETES FILES ON THE SERVER, NO STORAGE REQUIRED.
'''
from flask import Flask, render_template, request, send_from_directory, session
from flask_session import Session
from flask.helpers import url_for
import socketio
from spotdl.download import DownloadManager
from spotdl.parsers import parse_query
from spotdl.search import SpotifyClient, SongObject, from_spotify_url
import os
import shutil
import asyncio
from werkzeug.utils import redirect

# Initialize spotify client id & secret is provided by spotdl
SpotifyClient.init(
    client_id="5f573c9620494bae87890c0f08a60293",
    client_secret="212476d9b0f3472eaa762d90b19b0ba8",
    user_auth=False,
)

DIRNAME = os.path.dirname(__file__)

app = Flask(__name__)
app.secret_key = 'super secret key lmao'
app.config['SESSION_TYPE'] = 'redis'
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
            session['download_link'] = request.form.get('search')

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
            'album_cover_url': song_list[0].album_cover_url,            # str: url of img to cover album
            'file_name': song_list[0].file_name + '.mp3',               # str: file_name
            'list_of_artist_names': song_list[0].contributing_artists,  # str array: of contributing artists to track
            'album': song_list[0].album_name,                           # str: album name
            'duration': song_list[0].duration,                          # float: in seconds duraion of song
            'youtube_link': song_list[0].youtube_link                   # str:
        }

    # Handle Download
    if request.form.get('download_button') == 'Download':
        # Have to get download link again using AJAX for some reason
            # This downloads the song to current directory
        print("HELLLOOOOOOOO")
        print(f'{session["download_link"]}, {song_list}')

        #   If file already in uploads folder 
            #   --> Deletes file from current dir
            #   --> send user file in uploads folder
        if os.path.isfile(f'./uploads/{songObj["file_name"]}'):
            os.remove(songObj["file_name"])
        else:
            DownloadManager(spotdl_opts).download_multiple_songs(song_list)
            shutil.move(songObj["file_name"], './uploads/')

        return send_from_directory('./uploads/', songObj["file_name"], as_attachment=True)

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
            # If user input is a search query
            else:
                return redirect(url_for('search_page', search_query = search_input))

    if request.args.get('search_query', None) != None:
        session['search_query'] = request.args.get('search_query')

    # list[SongObject,...,SongObject]
    results_of_search_query = search_query(session['search_query'])

    # turn results_of_search_query into JSON
    results_of_search_query_json = {}
    for i in range(len(results_of_search_query)):
        # Filename doesn't include .mp3
        results_of_search_query_json[results_of_search_query[i].file_name] = {
            'album_cover_url': results_of_search_query[i].album_cover_url,
            'list_of_artists_names': results_of_search_query[i].contributing_artists,
            'duration':results_of_search_query[i].duration,
            'youtube_link':results_of_search_query[i].youtube_link,
            'spotify_link':results_of_search_query[i].spotify_url}

    return render_template('search_page.html', results_of_search_query=results_of_search_query_json)
    
def search_query(query: str):
    """
    THIS FUNCTION TAKES search query AS INPUT AND RETURN
    a `list<SongObject>`.
    """
    songs = []  # list<SongObjects>
    list_song_urls = []
    # get a spotify client
    spotify_client = SpotifyClient()

    search_results = spotify_client.search(query, type="track")

    number_of_search_results = len(search_results.get("tracks", {}).get("items", []))

    # return first result link or if no matches are found, raise Exception
    if search_results is None or number_of_search_results == 0:
        raise Exception("No song matches found on Spotify")

    # Adds each song url to list_song_urls
    for i in range(0, number_of_search_results):
        if search_results["tracks"]["items"][i]["id"] == None:
            break
        else:
            song_url = "http://open.spotify.com/track/" + search_results["tracks"]["items"][i]["id"]
            list_song_urls.append(song_url)

    # Create SongObject for each url in list_song_urls and add it to songs[]
    for i in range(len(list_song_urls)):
        song = from_spotify_url(list_song_urls[i], 'mp3', False, None, None)
        songs.append(song)

    return songs     

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5000)