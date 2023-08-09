# Django imports
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# AI model imports
import base64
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np
from sklearn.neighbors import NearestNeighbors

# Step 1: Set up Spotify API client
client_id = 'dd80a94f8bd34e47bcf020d0e975db1a'
client_secret = '8ab5a229184046b192ff3cb3445a3df9'
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Function to get song details from user input
def get_input_song_details():
    song_name = input("Enter the song name (type 'done' to stop): ")
    if song_name.lower() == 'done':
        return None
    results = sp.search(q=song_name, limit=1)

    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        artist_id = track['artists'][0]['id']
        
        # Retrieve artist details to get genres (if available)
        artist_info = sp.artist(artist_id)
        genres = artist_info.get('genres', [])  # Get genres if available, otherwise use an empty list
        
        return track_name, artist_name, track['id'], track['uri'], artist_id, genres
    else:
        print("Song not found.")
        return get_input_song_details()

# Step 2: Collect multiple input songs from the user
input_songs = []
while True:
    song_details = get_input_song_details()
    if song_details is None:
        break
    input_songs.append(song_details)

# Step 3: If input songs are available, find recommendations
if input_songs:
    for input_song, (song_name, artist_name, track_id, track_uri, artist_id, genres) in enumerate(input_songs):
        # Step 5: Get popular tracks with similar genres to the input artist
        related_tracks = []
        for genre in genres:
            tracks_by_genre = sp.search(q='genre:"' + genre + '"', type='track', limit=10)
            for track in tracks_by_genre['tracks']['items']:
                if track['popularity'] >= 50 and track['id'] != track_id:
                    related_tracks.append((track['name'], track['artists'][0]['name'], track['uri']))

        # If there are not enough related tracks, fetch other tracks by the same artist
        if len(related_tracks) < 5:
            tracks_by_artist = sp.artist_top_tracks(artist_id)
            for track in tracks_by_artist['tracks']:
                if track['id'] != track_id:
                    related_tracks.append((track['name'], track['artists'][0]['name'], track['uri']))

        # Step 6: Combine input song and related tracks for KNN
        all_tracks = [(song_name, artist_name, track_uri)] + related_tracks

        # Step 7: Create feature vectors for all tracks
        feature_vectors = []
        for _, _, uri in all_tracks:
            audio_features = sp.audio_features(uri)
            feature_vector = [audio_features[0]['danceability'], audio_features[0]['energy'],
                              audio_features[0]['key'], audio_features[0]['loudness'],
                              audio_features[0]['mode'], audio_features[0]['speechiness'],
                              audio_features[0]['acousticness'], audio_features[0]['instrumentalness'],
                              audio_features[0]['liveness'], audio_features[0]['valence'],
                              audio_features[0]['tempo']]
            feature_vectors.append(feature_vector)
        feature_vectors = np.array(feature_vectors)

        # Step 8: Fit the k-nearest neighbors model if there are enough related tracks
        n_neighbors = 6
        if len(all_tracks) >= n_neighbors:
            knn_model = NearestNeighbors(n_neighbors=n_neighbors, algorithm='auto', metric='euclidean')
            knn_model.fit(feature_vectors)

            # Step 9: Get the audio features of the input track
            audio_features = sp.audio_features(track_uri)
            input_feature_vector = [audio_features[0]['danceability'], audio_features[0]['energy'],
                                    audio_features[0]['key'], audio_features[0]['loudness'],
                                    audio_features[0]['mode'], audio_features[0]['speechiness'],
                                    audio_features[0]['acousticness'], audio_features[0]['instrumentalness'],
                                    audio_features[0]['liveness'], audio_features[0]['valence'],
                                    audio_features[0]['tempo']]
            input_feature_vector = np.array(input_feature_vector).reshape(1, -1)

            # Step 10: Find the KNN neighbors for the input track
            _, indices = knn_model.kneighbors(input_feature_vector)

            # Step 11: Add non-duplicate recommended tracks to the list
            recommended_tracks = []
            recommended_artists = []
            for i in indices.flatten()[1:]:  # Exclude the first index (input song itself)
                recommended_track, recommended_artist, recommended_uri = all_tracks[i]
                if (recommended_track, recommended_artist) not in input_songs and \
                   (recommended_track, recommended_artist) not in zip(recommended_tracks, recommended_artists):
                    recommended_tracks.append(recommended_track)
                    recommended_artists.append(recommended_artist)

            # Step 12: Display the details of the input song and the recommended songs
            print(f"Input Song {input_song + 1}:")
            print(f"Track: {song_name}, Artist: {artist_name}")
            print(f"Genres: {', '.join(genres)}")
            print("Recommended songs:")
            for i, (song_name, artist_name) in enumerate(zip(recommended_tracks, recommended_artists)):
                print(f"{i+1}. Track: {song_name}, Artist: {artist_name}")
            print("\n")

        else:
            print(f"Not enough related tracks for '{song_name}' by '{artist_name}'. Skipping recommendation for this input song.\n")

else:
    print("No input songs. Exiting...")


# Django API View
@api_view(['POST'])
def get_recommendations(request):
    input_songs = request.data.get('input_songs', [])

    # Your AI model code here
    recommendations = []
    for input_song, (song_name, artist_name, track_id, track_uri, artist_id, genres) in enumerate(input_songs):
        # Step 5: Get popular tracks with similar genres to the input artist
        related_tracks = []
        for genre in genres:
            tracks_by_genre = sp.search(q='genre:"' + genre + '"', type='track', limit=10)
            for track in tracks_by_genre['tracks']['items']:
                if track['popularity'] >= 50 and track['id'] != track_id:
                    related_tracks.append((track['name'], track['artists'][0]['name'], track['uri']))

        # If there are not enough related tracks, fetch other tracks by the same artist
        if len(related_tracks) < 5:
            tracks_by_artist = sp.artist_top_tracks(artist_id)
            for track in tracks_by_artist['tracks']:
                if track['id'] != track_id:
                    related_tracks.append((track['name'], track['artists'][0]['name'], track['uri']))

        # Step 6: Combine input song and related tracks for KNN
        all_tracks = [(song_name, artist_name, track_uri)] + related_tracks

        # Step 7: Create feature vectors for all tracks
        feature_vectors = []
        for _, _, uri in all_tracks:
            audio_features = sp.audio_features(uri)
            feature_vector = [audio_features[0]['danceability'], audio_features[0]['energy'],
                              audio_features[0]['key'], audio_features[0]['loudness'],
                              audio_features[0]['mode'], audio_features[0]['speechiness'],
                              audio_features[0]['acousticness'], audio_features[0]['instrumentalness'],
                              audio_features[0]['liveness'], audio_features[0]['valence'],
                              audio_features[0]['tempo']]
            feature_vectors.append(feature_vector)
        feature_vectors = np.array(feature_vectors)

        # Step 8: Fit the k-nearest neighbors model if there are enough related tracks
        n_neighbors = 6
        if len(all_tracks) >= n_neighbors:
            knn_model = NearestNeighbors(n_neighbors=n_neighbors, algorithm='auto', metric='euclidean')
            knn_model.fit(feature_vectors)

            # Step 9: Get the audio features of the input track
            audio_features = sp.audio_features(track_uri)
            input_feature_vector = [audio_features[0]['danceability'], audio_features[0]['energy'],
                                    audio_features[0]['key'], audio_features[0]['loudness'],
                                    audio_features[0]['mode'], audio_features[0]['speechiness'],
                                    audio_features[0]['acousticness'], audio_features[0]['instrumentalness'],
                                    audio_features[0]['liveness'], audio_features[0]['valence'],
                                    audio_features[0]['tempo']]
            input_feature_vector = np.array(input_feature_vector).reshape(1, -1)

            # Step 10: Find the KNN neighbors for the input track
            _, indices = knn_model.kneighbors(input_feature_vector)

            # Step 11: Add non-duplicate recommended tracks to the list
            recommended_tracks = []
            recommended_artists = []
            for i in indices.flatten()[1:]:  # Exclude the first index (input song itself)
                recommended_track, recommended_artist, recommended_uri = all_tracks[i]
                if (recommended_track, recommended_artist) not in input_songs and \
                   (recommended_track, recommended_artist) not in zip(recommended_tracks, recommended_artists):
                    recommended_tracks.append(recommended_track)
                    recommended_artists.append(recommended_artist)

            # Step 12: Append recommendations to the list
            recommendations.append({
                "input_song": input_song + 1,
                "track": song_name,
                "artist": artist_name,
                "genres": genres,
                "recommended_songs": [{"track": t, "artist": a} for t, a in zip(recommended_tracks, recommended_artists)]
            })

    return Response({"recommendations": recommendations}, status=status.HTTP_200_OK)
