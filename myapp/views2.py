# views.py
# python manage.py runserver


from django.shortcuts import render
import base64
import requests


def library(request):
    return render(request, 'library.html')

def home(request):
    if request.user.is_authenticated:
        username = request.user.username
    else:
        username = 'Guest'
    return render(request, 'home.html', {'username': username})

def search_artists(request):
    if request.method == 'POST':
        song_query = request.POST.get('song_query')

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
        params = {
            'q': song_query,
            'type': 'artist',
            'limit': 12  # Number of search results to retrieve
        }
        response = requests.get(api_url, headers=headers, params=params)
        search_results = response.json()
        
        if 'artists' in search_results:
            artists = search_results['artists']['items']
            if len(artists) > 0:
                context = {'artists': artists}
            else:
                context = {'error_message': 'No search results found.'}
        else:
            context = {'error_message': 'An error occurred during the search.'}


        return render(request, 'search_artist_results.html', context)

    return render(request, 'search_artist.html')


def search_results(request):
    if request.method == 'POST':
        song_query = request.POST.get('song_query')

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
        params = {
            'q': song_query,
            'type': 'track',
            'limit': 5  # Number of search results to retrieve
        }
        response = requests.get(api_url, headers=headers, params=params)
        search_results = response.json()

        # Extract and prepare the search results
        tracks = []
        if 'tracks' in search_results:
            tracks = search_results['tracks']['items']

        context = {
            'tracks': tracks
        }

        return render(request, 'search_results.html', context)

    return render(request, 'search_form.html')
