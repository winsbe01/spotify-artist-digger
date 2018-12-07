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

    attr_to_id_map = {}
    for track in tracks_analysis.keys():
        a = tracks_analysis[track][0][attribute]
        if a in attr_to_id_map:
            attr_to_id_map[a].append(track)
        else:
            attr_to_id_map[a] = [track]
    return attr_to_id_map
    
def track_map(tracks_analysis, attribute):
    id_to_attr_map = {}
    for track in tracks_analysis.keys():
        id_to_attr_map[track] = tracks_analysis[track][0][attribute]

def attr_maps(tracks_analysis, attribute):
    # initialize maps
    attr_to_id_map = {}
    id_to_attr_map = {}

    for track in tracks_analysis.keys():
        # get the desired attribute
        a = tracks_analysis[track][0][attribute]
        
        # assign id to the attribute
        id_to_attr_map[track] = a

        if a in attr_to_id_map:
            attr_to_id_map[a].append(track)
        else:
            attr_to_id_map[a] = [track]

    return (attr_to_id_map, id_to_attr_map)

def attr_median(attr_maps):
    # find the median
    med = statistics.median(list(attr_maps[1].values()))
    return attr_maps[0][med]

def attr_mean(attr_map):
    # calculate the mean
    return round(statistics.mean(attr_map.keys()),3)

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
    
# calculate the difference from the median for the given attribute
def obj_median(track_analysis, attribute):
    attr_list = map(lambda x: track_analysis[x][0][attribute], track_analysis.keys())
    med = statistics.median(attr_list)
    
    ret = {}
    for track in track_analysis.keys():
        ret[track] = abs(round(track_analysis[track][0][attribute] - med,8))

    return ret

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
for album in albums:
    track_uris.extend(track_list_uris(sp, album))
print(len(track_uris), "songs total...")
print("Getting track analysis...")

# analyze the tracks
track_analysis = {}
for track in track_uris:
    track_analysis[track] = sp.audio_features(track)

# run medians on all our vectors
danceabilities = obj_median(track_analysis, 'danceability')
energies = obj_median(track_analysis, 'energy')
speechiness = obj_median(track_analysis, 'speechiness')
acousticness = obj_median(track_analysis, 'acousticness')
instrumentalness = obj_median(track_analysis, 'instrumentalness')
liveness = obj_median(track_analysis, 'liveness')
valence = obj_median(track_analysis, 'valence')

# sum up all medians per track
track_sums = {}
for track in track_uris:
    track_sums[track] = danceabilities[track] + energies[track] + speechiness[track] + acousticness[track] + instrumentalness[track] + liveness[track] + valence[track]

# calculate the min and max
mn = min(track_sums.values())
mnurl = None
mx = max(track_sums.values())
mxurl = None
for track in track_uris:
    if track_sums[track] == mn:
        mnurl = track
    if track_sums[track] == mx:
        mxurl = track
print("Most median song:", track_string(sp, mnurl))
print("Least median song:", track_string(sp, mxurl))
