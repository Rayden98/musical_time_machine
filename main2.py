from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# ------------------------------------ CONSTANTS ---------------------------------------------------#
SPOTIFY_CLIENT_ID = "4b7f98cf1f4f45c8b867f3f24bfcf0b3"
SPOTIFY_SECRET = "4a6d8c32310548e8ac1ffb7c1a3161fc"
REDIRECT_URL = "http://localhost:8888/callback"

DATE_SONG = input("Which year do you want to travel to? Type the date in this format: YYY-MM-DD: ")
SONG_YEAR_YEAR = DATE_SONG.split("-")[0]

# ----------------------------------SEARCHING THE SONGS ---------------------------------------------#
response = requests.get(f"https://www.billboard.com/charts/hot-100/{DATE_SONG}/")
web_page = response.text

soup = BeautifulSoup(web_page, "html.parser")

song_tag_track = soup.findAll(name="h3", id="title-of-a-story", class_="a-no-trucate")
song_tag_artist = soup.findAll(name="span", class_="a-no-trucate")
#print(song_tag_artist)
#print(song_tag_track)

# ---------------------PUTTING THE INFORMATION IN THE DICTIONARY -----------------------------------#
my_dict = {}

number = 0
my_list1 = []
for each in song_tag_track:
    number += 1
    artist = each.getText().strip()
    my_list1.append(artist)

my_dict["songs"] = my_list1
#print(my_dict)

my_list2 = []
for each in song_tag_artist:
    number += 1
    track = each.getText().strip()
    my_list2.append(track)

my_dict["artists"] = my_list2

#result = pd.DataFrame.from_dict(my_dict)
#print(result)

# --------------------------------SEARCHING THE TRACKS ---------------------------------------------#
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri=REDIRECT_URL,
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_SECRET,
        cache_path="token.txt"
    )
)

#
new_dic = [{'song': song, 'artist': artist} for song, artist in zip(my_dict['songs'], my_dict['artists'])]

new_songs = []
number_goods = 0
number_bads = 0
#year:{SONG_YEAR_YEAR}
for each in new_dic:
    try:
        spotify_result = sp.search(q=f"artist:{each['artist']} track:{each['song']}", type="track")
        #print(spotify_result)
        song_uri = spotify_result['tracks']['items'][0]['uri']
        #print(song_uri)
        new_songs.append(song_uri.split(":")[2])
        print(song_uri.split(":")[2])
        #print(new_songs)
        number_goods += 1
    except IndexError:
        number_bads +=1
        pass

#print(number_goods)
#print(number_bads)

# -----------------------------------CREATING THE PLAYLIST -----------------------------------------#

results = sp.current_user()
user_id = results['id']
playlist = sp.user_playlist_create(user=f"{user_id}", name=f"Billboard Top Tracks {SONG_YEAR_YEAR}", public=False,
                                      description="Top Tracks from back in the Dayz")
playlist_id = playlist["id"]


# ---------------------------ADDING THE TRACKS  INSIDE THE PLAYLIST----------------------------------#
sp.user_playlist_add_tracks(playlist_id=playlist_id, user=f"{user_id}", tracks=new_songs)


