import requests
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Movie
from datetime import datetime

def fetch_movie_from_tmdb(title):
    """Fetch movie data from TMDb by title and save to Movie model."""
    base_url = "https://api.themoviedb.org/3"
    search_url = f"{base_url}/search/movie"
    details_url = f"{base_url}/movie/{{movie_id}}"
    providers_url = f"{base_url}/movie/{{movie_id}}/watch/providers"
    
    # Search for the movie by title
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': title,
        'language': 'en-US'
    }
    
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if not data['results']:
        return None
    
    movie_data = data['results'][0]
    movie_id = movie_data['id']
    
    # Fetch detailed movie info
    details_response = requests.get(details_url.format(movie_id=movie_id), params={'api_key': settings.TMDB_API_KEY, 'language': 'en-US'})
    details_response.raise_for_status()
    details = details_response.json()
    
    # Fetch streaming providers (region-specific, e.g., 'US')
    providers_response = requests.get(providers_url.format(movie_id=movie_id), params={'api_key': settings.TMDB_API_KEY})
    providers_response.raise_for_status()
    providers = providers_response.json()
    
    # Get watch link (prioritize 'homepage' or first streaming provider)
    watch_link = details.get('homepage', '')
    if not watch_link and 'results' in providers and 'US' in providers['results']:
        provider_data = providers['results']['US'].get('flatrate', [])
        if provider_data:
            watch_link = provider_data[0].get('link', '')  # First provider link
    
    # Save to Movie model
    movie, created = Movie.objects.get_or_create(
        title=details['title'],
        defaults={
            'release_date': datetime.strptime(details['release_date'], '%Y-%m-%d').date() if details['release_date'] else None,
            'runtime': details['runtime'] if details['runtime'] else 0,
            'description': details['overview'],
            'watch_link': watch_link
        }
    )
    
    # Fetch and save poster image
    if details['poster_path']:
        poster_url = f"https://image.tmdb.org/t/p/w500{details['poster_path']}"
        image_response = requests.get(poster_url)
        if image_response.status_code == 200:
            movie.image.save(f"{details['title']}_poster.jpg", ContentFile(image_response.content), save=True)
    
    return movie