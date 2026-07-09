from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # GitHub Pages එකෙන් call කරන්න පුළුවන් වෙන්න

# ===== CONFIG =====
OMDB_API_KEY = '7a316873'  # උබේ OMDb Key එක
CINESUBZ_BASE = 'https://cinesubz.co'

# ===== HELPER FUNCTIONS =====
def get_omdb_data(imdb_id=None, title=None):
    """OMDb API එකෙන් movie details ගන්න"""
    try:
        if imdb_id:
            url = f'http://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}&plot=full'
        elif title:
            url = f'http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}&plot=full'
        else:
            return None
        
        res = requests.get(url, timeout=10)
        data = res.json()
        
        if data.get('Response') == 'True':
            return data
        return None
    except Exception as e:
        print(f"OMDb Error: {e}")
        return None

def scrape_cinesubz_video(imdb_id):
    """CineSubz එකෙන් video link එක හොයනවා"""
    try:
        # 1. CineSubz search
        search_url = f'{CINESUBZ_BASE}/?s={imdb_id}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 2. First result එකේ link එක ගන්න
        first_post = soup.select_one('article.post h2.entry-title a')
        if not first_post:
            return None
            
        post_url = first_post['href']
        
        # 3. Post එකට ගිහින් video link එක හොයනවා
        res = requests.get(post_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Download buttons හොයනවා
        dl_buttons = soup.select('a.download-button, a[href*=".mp4"], a[href*=".mkv"]')
        
        video_url = None
        subtitle_url = None
        whatsapp_url = None
        
        for btn in dl_buttons:
            href = btn.get('href', '')
            text = btn.get_text().lower()
            
            if '.mp4' in href or '.mkv' in href:
                if 'sub' in text or 'සිංහල' in text:
                    subtitle_url = href
                else:
                    video_url = href
            
            if 'whatsapp' in href or 'wa.me' in href:
                whatsapp_url = href
        
        # Video URL එක නැත්නම් iframe හොයනවා
        if not video_url:
            iframe = soup.select_one('iframe[src*="player"], iframe[src*="embed"]')
            if iframe:
                video_url = iframe['src']
        
        if video_url:
            return {
                'name': 'CineSubz',
                'videoUrl': video_url,
                'subtitleUrl': subtitle_url,
                'whatsappDownloadUrl': whatsapp_url
            }
        return None
        
    except Exception as e:
        print(f"CineSubz Error: {e}")
        return None

# ===== API ROUTES =====

@app.route('/')
def home():
    return jsonify({'status': 'Cinemax API Running', 'version': '1.0'})

@app.route('/api/omdb', methods=['GET'])
def omdb_route():
    """OMDb details දෙනවා"""
    imdb_id = request.args.get('i')
    title = request.args.get('t')
    
    if not imdb_id and not title:
        return jsonify({'success': False, 'error': 'IMDb ID or Title required'}), 400
    
    data = get_omdb_data(imdb_id=imdb_id, title=title)
    
    if data:
        return jsonify({'success': True, 'data': data})
    else:
        return jsonify({'success': False, 'error': 'Movie not found'}), 404

@app.route('/api/video/<imdb_id>', methods=['GET'])
def video_route(imdb_id):
    """Video link එක දෙනවා"""
    season = request.args.get('season')
    episode = request.args.get('episode')
    
    # Series නම් season/episode handle කරන්න ඕන. දැනට movie විතරයි
    data = scrape_cinesubz_video(imdb_id)
    
    if data:
        return jsonify({'success': True, 'data': data})
    else:
        return jsonify({'success': False, 'error': 'Video not found'}), 404

@app.route('/api/search', methods=['GET'])
def search_route():
    """OMDb search"""
    query = request.args.get('q')
    if not query:
        return jsonify({'success': False, 'error': 'Query required'}), 400
    
    try:
        url = f'http://www.omdbapi.com/?s={query}&apikey={OMDB_API_KEY}'
        res = requests.get(url, timeout=10)
        data = res.json()
        
        if data.get('Response') == 'True':
            # Frontend එකට ඕන format එකට හදනවා
            results = []
            for item in data.get('Search', [])[:10]:
                results.append({
                    'title': item.get('Title'),
                    'image': item.get('Poster') if item.get('Poster') != 'N/A' else '',
                    'rating': item.get('Year'),
                    'imdbID': item.get('imdbID')
                })
            return jsonify({'success': True, 'data': results})
        else:
            return jsonify({'success': True, 'data': []})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
