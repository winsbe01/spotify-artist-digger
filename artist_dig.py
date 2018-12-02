#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3

import spotipy
import spotipy.util as sutil
import statistics

def authorize():
    
    # setup the secrets, etc
    s_username='yourusername'
    s_scope='user-library-read'
    s_client_id='yourclientID'
    s_client_secret='yourclientsecret'
    s_redirect_url='yourredirecturl'

    # try and get a token
    token = sutil.prompt_for_user_token(s_username,s_scope,s_client_id,s_client_secret,s_redirect_url)

    # if we get one, return a spotify object
    if token:
        return spotipy.Spotify(auth=token)
    else:
        return None

def artist_search(sp):
    # get the search query
    q = input("Artist: ")

    # search for the artist
    res = sp.search(q,type='artist')

    # print out numbered list of artists
    artists = {}
    idx = 0
    for artist in res['artists']['items']:
        artists[idx] = artist['uri']
        print('(' + str(idx) + ')', artist['name'])
        idx = idx + 1

    # let the user choose who they meant, default to the first pick
    choice = input("Choose [0]: ")
    if choice == "":
        choice = 0

    return artists[int(choice)]

def album_list_uris(sp, artist):
    res = sp.artist_albums(artist,album_type='album')
    uris = []
    for album in res['items']:
        uris.append(album['uri'])
    return uris

def track_list_uris(sp, album):
    res = sp.album_tracks(album)
    uris = []
    for track in res['items']:
        uris.append(track['uri'])
    return uris

def track_string(sp, uri):
    track_info = sp.track(uri)
    return str(track_info['name']) + " (" + str(track_info['album']['name']) + ", track " + str(track_info['track_number']) + ")"

def attr_mean_calc(tracks_analysis, attribute):
    # assemble list of targeted attribute
    attr_list = []
    for track in tracks_analysis.keys():
        attr_list.append(tracks_analysis[track][0][attribute])

    # calculate the mean
    attr_mean = round(statistics.mean(attr_list),3)

    # calculate the diffs
    attr_diffs = map(lambda x: abs(round(attr_mean - x,3)), attr_list)

    # calculate the smallest difference
    attr_diff_min = min(list(attr_diffs))

    # find the targeted track(s)
    track_list = []
    for track in tracks_analysis.keys():
        track_attr_diff = round(tracks_analysis[track][0][attribute] - attr_mean, 3)
        if abs(track_attr_diff) == attr_diff_min:
            track_list.append(track)

    return track_list
    
"""
Main Running Code
"""

# do the authorization
sp = authorize()

# get the artist
artist = artist_search(sp)

# get the albums
albums = album_list_uris(sp, artist)
print("Found", len(albums), "albums...")

# get the tracks
track_uris = []
#for album in albums_res:
    #print(item['name'] + ' - ' + item['uri'] + ' - ' + str(item['available_markets']))

for album in albums:
    track_uris.extend(track_list_uris(sp, album))
    #tracks_res = sp.album_tracks(album)['items']
    #for track in tracks_res:
    #    track_uris.append(track['uri'])
    #print(item['name'])

print(len(track_uris), "songs total...")

print("Getting track analysis...")

#print(track_uris)
track_analysis = {}
for track in track_uris:
    track_analysis[track] = sp.audio_features(track)

mean_tempo_list = attr_mean_calc(track_analysis, 'tempo')
print("Mean tempo:", track_string(sp, mean_tempo_list[0]))
#print(sp.track(mean_tempo_list[0])['name'])

mean_dance_list = attr_mean_calc(track_analysis, 'danceability')
print("Mean dancibility:", track_string(sp, mean_dance_list[0]))

mean_energy_list = attr_mean_calc(track_analysis, 'energy')
print("Mean energy:", track_string(sp, mean_energy_list[0]))

"""
tempo_map = {}
tempo_list = []
for track_uri in track_uris:
    tempo_map[track_uri] = track_analysis[track_uri][0]['tempo']
    tempo_list.append(track_analysis[track_uri][0]['tempo'])

tempo_mean = round(statistics.mean(tempo_list),3)

tempo_diffs = map(lambda x: abs(round(tempo_mean - x,3)), tempo_list)

tempo_diff_min = min(list(tempo_diffs))

for track_uri in track_uris:
    cur_tempo = tempo_map[track_uri]
    if abs(round(cur_tempo - tempo_mean,3)) == tempo_diff_min:
        print(track_uri)
"""
