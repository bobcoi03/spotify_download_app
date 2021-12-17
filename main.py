''' 
    USER TYPES IN SPOTIFY LINK
    AND SITE DOWNLOADS FILES TO SERVER, 
    THEN SENDS THAT FILE TO USER AND THEN
    DELETES FILES ON THE SERVER, NO STORAGE REQUIRED.
'''
import subprocess
import sys
from flask import Flask, render_template, request, send_from_directory
import subprocess
import sys # for sys.executable (The file path of the currently using python)
from spotdl import __main__ as spotdl # To get the location of spotdl

app = Flask(__name__)

@app.route("/", methods = ['GET','POST'])
def main():

    # get spotify link and download it
    if request.method == 'POST':

        spotify_link = request.form.get('spotify_link')

        # Add security features here, make sure link is true
        subprocess.check_call([sys.executable, spotdl.__file__, spotify_link])

        # User download files
        return send_from_directory(path_to_file, filename, as_attachment=True)

    return render_template('main.html')


