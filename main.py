import requests
import urllib.parse
import os
import google_auth_oauthlib
import google_auth_oauthlib.flow
import googleapiclient.discovery
import youtube_dl

import spotify_token as st
data = st.start_session("AQBN8rX39HHLIt0EwUYVTa0Nlfq9d83AWWfbXNfkfivaEE_5a1IsjEOAQtuMdNv-NLSqwMEWQSt7RewZXGDZSpfq7unp8gZWaCPzdkNx36k","fb74f62d-426b-4606-a5bd-1e0f367f2083")
access_token = data[0]   # spotify api token
expiration_date = data[1]  # only valid for 1 year


class Playlist():
    def __init__(self, id, title):
        self.id = id
        self.title = title


class Song():
    def __init__(self,artist,name):
        self.name = name
        self.artist = artist


class YoutubeClient():
    def __init__(self, credential_location):
        # youtube_dl default User-Agent can cause some json values to return as None, using Facebook's web crawler solves this.
        youtube_dl.utils.std_headers['User-Agent'] = "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"

        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        # Disable OAuthlib's HTTPS verification when running locally.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"


        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(credential_location, scopes)
        credentials = flow.run_console()
        youtube_client = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


        self.youtube_client = youtube_client


    def get_playlists(self):
        request = self.youtube_client.playlists().list(
            part="id, snippet",
            maxResults=50,
            mine=True
        )
        response = request.execute()

        playlists = [Playlist(item['id'], item['snippet']['title']) for item in response['items']]

        return playlists



    def get_vid(self,playlist_id):
        song_lst = []
        request = self.youtube_client.playlistItems().list(
            playlistId=playlist_id,
            part="id, snippet",
            maxResults=50
        )

        response = request.execute()

        for item in response['items']:
            vid_id = item['snippet']['resourceId']['videoId']
            artist, name = self.get_artist_and_song_name(vid_id)
            if artist and name:
                song_lst.append(Song(artist,name))

        return song_lst


    def get_artist_and_song_name(self,vid_id):
        url = f"https://www.youtube.com/watch?v={vid_id}"

        video = youtube_dl.YoutubeDL({"quiet": True}).extract_info(
            url,
            download=False
        )

        artist = video['artist']
        track = video['track']

        return artist, track


class Spotify(object):
    def __init__(self,api_token):  # api token required to search for song in spotify
        self.api_token = api_token


    def search_song(self, artist, track):
        query = urllib.parse.quote(f'{artist} {track}')
        url = f"https://api.spotify.com/v1/search?q={query}&type=track"
        response = requests.get(                                # searching a song
            url,
            headers={
                "Content-type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )
        response_json = response.json()

        results = response_json['tracks']['items']

        if results:
            return results[0]['id']      # return the first search on spotify
        else:
            raise Exception(f"No Sound Found")

    def add_song_to_playlist(self, song_id):
        url = "https://api.spotify.com/v1/me/tracks"
        response = requests.put(
            url,
            json={
                "ids": [song_id]
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
        )

        return response.ok



def main():
    # downlaod the youtube credentals file and place in the cred directory

    youtube_client = YoutubeClient('./creds/client_secret.json')
    spotify_client = Spotify(access_token)
    playlists = youtube_client.get_playlists()


    for i, playlist in enumerate(playlists):
        print(f"{i}: {playlist.title}")   # get playlist name and its index
    choice = int(input("Enter your choice: "))
    chosen_playlist = playlists[choice]
    print("Playlist chosen: " + str(chosen_playlist.title))


    # retrieveing song info from playlist
    songs = youtube_client.get_vid(chosen_playlist.id)
    print("adding " + str(len(songs)) + " songs")

    for song in songs:
        spotify_song_id = spotify_client.search_song(song.artist, song.name)
        if spotify_song_id:
            added = spotify_client.add_song_to_playlist(spotify_song_id)
            if added:
                print ("added " + str(song.name))
            else:
                continue



main()