# spotify_download_app
Convert spotify link to mp3 using spotdl

WE SHOULD ADD A SEARCH FUNCTION THAT DISPLAYS SONGS, BECAUSE IT'S MORE CONVENIENT, RATHER THAN COPYING IN URL.

spotdl.search.song_gatherer.from_search_term() = """
    Queries Spotify for a song and returns the best match

    `str` `query` : what you'd type into Spotify's search box
    `str` `output_format` : output format of the song

    returns a `list<SongObject>` containing Url's of each track in the given album

    But this only returns the first song in search.

    IDEALLY WE NEED TO MAKE THIS SEARCH FUNCTION REAL TIME DISPLAYING CHANGES AS THE INPUT CHANGES.

    GAMEPLAN: 

    run 

    OUR FUNC SHOULD TAKE QUERY AS INPUT AND RETURN `list<SongObject>` of length 5 or more.

    spotdl.search.song_gatherer.from_spotify_url() takes one spotify url as input and returns one SongObject

    SpotifyClient.search(query, type="tracks")


    """

SEARCH_QUERY() IN MAIN.PY IS SLOW BECAUSE IT CREATES A SONGOBJECT FOR EACH SEARCH RESULT


