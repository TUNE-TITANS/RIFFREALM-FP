# views.py
# python manage.py runserver

from django.shortcuts import render, redirect
from django.shortcuts import render
import base64
import requests
import json
from django.http import JsonResponse
from django.contrib.sessions.models import Session



def library(request):
    return render(request, 'library.html')

def signout(request):
    return render(request, 'home.html')

def home(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = 'Guest'
    return render(request, 'home.html', {'username': username})


from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from django.http import JsonResponse

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            error_message = 'Username already exists!'
            return render(request, 'signup.html', {'error_message': error_message})
        else:
            hashed_password = make_password(password)
            user = User(username=username, password=hashed_password)
            user.save()
            return redirect('signin')
    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if check_password(password, user.password):
                return redirect('Dashboard')
            else:
                error_message = 'Invalid username or password'
                return render(request, 'signin.html', {'error_message': error_message})
        except User.DoesNotExist:
            error_message = 'Invalid username or password'
            return render(request, 'signin.html', {'error_message': error_message})
    else:
        return render(request, 'signin.html')

def Dashboard(request):
    # You can retrieve any required user data here and pass it to the dashboard template
    if request.method == 'POST':
        query = request.POST.get('song_query')

        # Step 1: Construct the Authorization Header
        client_id = 'dd80a94f8bd34e47bcf020d0e975db1a'
        client_secret = '8ab5a229184046b192ff3cb3445a3df9'
        auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()

        # Step 2: Make the Token Request
        token_url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}
        response = requests.post(token_url, headers=headers, data=data)

        # Step 3: Handle the Token Response
        response_json = response.json()
        access_token = response_json['access_token']

        # Step 4: Use the Access Token in subsequent API requests
        api_url = 'https://api.spotify.com/v1/search'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        artist_params = {
            'q': query,
            'type': 'artist',
            'limit': 5  # Number of artist search results to retrieve
        }
        track_params = {
            'q': query,
            'type': 'track',
            'limit': 5  # Number of track search results to retrieve
        }
        album_params = {
            'q': query,
            'type': 'album',
            'limit': 5  # Number of album search results to retrieve
        }
        
        # Search for artists
        artist_response = requests.get(api_url, headers=headers, params=artist_params)
        artist_search_results = artist_response.json()
        artists = []
        if 'artists' in artist_search_results:
            artists = artist_search_results['artists']['items']

        # Search for tracks
        track_response = requests.get(api_url, headers=headers, params=track_params)
        track_search_results = track_response.json()
        tracks = []
        if 'tracks' in track_search_results:
            tracks = track_search_results['tracks']['items']
        
        # Search for albums
        album_response = requests.get(api_url, headers=headers, params=album_params)
        album_search_results = album_response.json()
        albums = []
        if 'albums' in album_search_results:
            albums = album_search_results['albums']['items']

        context = {
            'artists': artists,
            'tracks': tracks,
            'albums': albums
        }

        return render(request, 'search_results.html', context)

    return render(request, 'Dashboard.html')

def recommendation(request):
    if request.method == 'POST':
        favoritetracks_cookie = request.COOKIES.get('favoritetracks')
        favoritetracks_localstorage = request.POST.get('favoritetracks')

        if favoritetracks_localstorage:
            favoritetracks = json.loads(favoritetracks_localstorage)
        elif favoritetracks_cookie:
            favoritetracks = json.loads(favoritetracks_cookie)
        else:
            favoritetracks = []

        request_data = [{"song_name": track["name"], "artist_name": track["artist"]} for track in favoritetracks]

        response = requests.post('https://music-recommendation23-986ec1dfcc36.herokuapp.com/recommend', json=request_data)

        if response.status_code == 200:
            recommended_songs = response.json()["recommended_songs"]
        else:
            recommended_songs = []

        context = {
            'recommended_songs': recommended_songs
        }
        

        return render(request, 'recommendations.html', context)

    return render(request, 'recommendations.html')

def create_playlist(request):
    
    return render(request, 'create_playlist.html')

def search(request):
   if request.method == 'POST':
        query = request.POST.get('song_query')

        # Step 1: Construct the Authorization Header
        client_id = 'dd80a94f8bd34e47bcf020d0e975db1a'
        client_secret = '8ab5a229184046b192ff3cb3445a3df9'
        auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()

        # Step 2: Make the Token Request
        token_url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}
        response = requests.post(token_url, headers=headers, data=data)

        # Step 3: Handle the Token Response
        response_json = response.json()
        access_token = response_json['access_token']

        # Step 4: Use the Access Token in subsequent API requests
        api_url = 'https://api.spotify.com/v1/search'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        artist_params = {
            'q': query,
            'type': 'artist',
            'limit': 12  # Number of artist search results to retrieve
        }
        track_params = {
            'q': query,
            'type': 'track',
            'limit': 5  # Number of track search results to retrieve
        }
        
        # Search for artists
        artist_response = requests.get(api_url, headers=headers, params=artist_params)
        artist_search_results = artist_response.json()
        artists = []
        if 'artists' in artist_search_results:
            artists = artist_search_results['artists']['items']

        # Search for tracks
        track_response = requests.get(api_url, headers=headers, params=track_params)
        track_search_results = track_response.json()
        tracks = []
        if 'tracks' in track_search_results:
            tracks = track_search_results['tracks']['items']

        context = {
            'artists': artists,
            'tracks': tracks
        }

        return render(request, 'search_results.html', context)

def songs(request):
    if request.method == 'POST':
        query = request.POST.get('song_query')

        # Step 1: Construct the Authorization Header
        client_id = 'dd80a94f8bd34e47bcf020d0e975db1a'
        client_secret = '8ab5a229184046b192ff3cb3445a3df9'
        auth_header = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()

        # Step 2: Make the Token Request
        token_url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'grant_type': 'client_credentials'}
        response = requests.post(token_url, headers=headers, data=data)

        # Step 3: Handle the Token Response
        response_json = response.json()
        access_token = response_json['access_token']

        # Step 4: Use the Access Token in subsequent API requests
        api_url = 'https://api.spotify.com/v1/search'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        track_params = {
            'q': query,
            'type': 'track',
            'limit': 5  # Number of track search results to retrieve
        }
        
        # Search for tracks (songs)
        track_response = requests.get(api_url, headers=headers, params=track_params)
        track_search_results = track_response.json()
        tracks = []
        if 'tracks' in track_search_results:
            tracks = track_search_results['tracks']['items']

        context = {
            'tracks': tracks
        }

        return render(request, 'tracks.html', context)

    return render(request, 'Dashboard.html')
