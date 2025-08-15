import os
import json
import requests


CACHE_DIR = 'cache'
_cache = {}

def get(name, url):
    if name in _cache:
        print(f"Using cached data for {name}")
        return _cache[name]
    
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"{name}.json")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched data for {name}")
        _cache[name] = data
        return data
    except requests.RequestException as e:
        print(f"Error fetching data for {name}: {e}")
        if os.path.exists(cache_path):
            print(f"Using cached data for {name} from {cache_path}")
            with open(cache_path, 'r') as f:
                data = json.load(f)
            _cache[name] = data
            return data
        else:
            raise RuntimeError(f"Failed to fetch data for {name} and no cache available") from e
        