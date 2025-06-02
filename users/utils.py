# movies/utils.py
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Movie
from datetime import datetime

def fetch_movie_from_tmdb(title):
    print("Searching TMDb for:", title)
    base_url = "https://api.themoviedb.org/3"
    search_url = f"{base_url}/search/movie"
    details_url = f"{base_url}/movie/{{movie_id}}"
    providers_url = f"{base_url}/movie/{{movie_id}}/watch/providers"
    
    params = {'api_key': settings.TMDB_API_KEY, 'query': title, 'language': 'en-US'}
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        print("Search results:", data.get('results', []))
        
        if not data.get('results'):
            print("No results found for:", title)
            return None
        
        movie_data = data['results'][0]
        movie_id = movie_data['id']
        print("Movie ID:", movie_id)
        
        details_response = requests.get(details_url.format(movie_id=movie_id), params={'api_key': settings.TMDB_API_KEY, 'language': 'en-US'})
        details_response.raise_for_status()
        details = details_response.json()
        print("Movie details:", details)
        
        watch_link = details.get('homepage', '')
        providers_response = requests.get(providers_url.format(movie_id=movie_id), params={'api_key': settings.TMDB_API_KEY})
        if providers_response.status_code == 200:
            providers = providers_response.json()
            print("Providers:", providers)
            if 'results' in providers and 'US' in providers['results']:
                provider_data = providers['results']['US'].get('flatrate', [])
                if provider_data:
                    watch_link = provider_data[0].get('link', watch_link)
        
        movie, created = Movie.objects.get_or_create(
            title=details['title'],
            defaults={
                'release_date': datetime.strptime(details['release_date'], '%Y-%m-%d').date() if details.get('release_date') else None,
                'runtime': details.get('runtime', 0),
                'description': details.get('overview', ''),
                'watch_link': watch_link,
            }
        )
        # Ensure last_searched is updated
        movie.last_searched = datetime.now()
        movie.save()
        # print("Movie saved:", movie.title, "Created:", created, "Last Searched:", movie.last_searched)
        
        if details.get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w500{details['poster_path']}"
            image_response = requests.get(poster_url)
            if image_response.status_code == 200:
                movie.image.save(f"{details['title']}_poster.jpg", ContentFile(image_response.content), save=True)
                print("Image saved for:", movie.title)
            else:
                print("Failed to download image:", poster_url)
        
        return movie
    except requests.RequestException as e:
        print("API error:", str(e))
        return None