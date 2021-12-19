''' 
    USER TYPES IN SPOTIFY LINK
    AND SITE DOWNLOADS FILES TO SERVER, 
    THEN SENDS THAT FILE TO USER AND THEN
    DELETES FILES ON THE SERVER, NO STORAGE REQUIRED.
'''
from flask import Flask, render_template, request, send_from_directory
from spotdl.download import DownloadManager
from spotdl.parsers import parse_query
from spotdl.search import SpotifyClient, SongObject
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

@app.route("/", methods = ['GET','POST'])
def main():

    # 
    songObj = {}

    # get spotify link and download it
    if request.method == 'POST':

        spotify_link = request.form.get('search')

        spotdl_opts = {
            "query": [str(spotify_link)],
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

        songObj = {
            'album_cover_url': song_list[0].album_cover_url,
            'file_name': song_list[0].file_name + '.mp3',
            'list_of_artist_names': song_list[0].contributing_artists,
            'album': song_list[0].album_name,
            'duration': song_list[0].duration
        }

        # Downloads song        
        DownloadManager(spotdl_opts).download_multiple_songs(song_list)
        # Move file from current folder into /uploads/ Because I don't know how to do it in spotDL
    
        # Check if file_name already exists in /uploads folder
        if os.path.isfile(f'./uploads/{songObj["file_name"]}'):
            os.remove(songObj["filename"])
            return send_from_directory('./uploads/', songObj["filename"], as_attachment=True)
        else:
            shutil.move(songObj["filename"], './uploads/')

            return send_from_directory('./uploads/', songObj["filename"], as_attachment=True)

    return render_template('main.html', songObj = songObj)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



