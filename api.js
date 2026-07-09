// api.js
const API_BASE = 'https://your-api-name.onrender.com/api'; // Render URL එක දාන්න

// ===== STATIC DATA =====
export const CATEGORIES = {
  trending: ['tt0241527','tt0295297','tt0304141','tt4633694','tt28212876','tt11198330','tt9813792','tt13443470','tt10919420','tt4574334','tt0903747'],
  hollywood: ['tt0241527','tt0295297','tt0304141','tt4633694','tt28212876','tt0111161','tt1375666','tt0816692','tt0468569'],
  kdrama: ['tt15266542','tt14689414','tt13370348','tt11280740','tt10262630'],
  bollywood: ['tt8178634','tt15327088','tt12735488','tt1187043','tt12844910'],
  sinhala: ['tt2386490','tt0111161','tt1375666']
};

export const LANG_MAP = {
  'en': {flag:'🇬🇧', name:'English'},
  'si': {flag:'🇱🇰', name:'Sinhala'},
  'ta': {flag:'🇱🇰', name:'Tamil'},
  'ko': {flag:'🇰🇷', name:'Korean'},
  'hi': {flag:'🇮🇳', name:'Hindi'}
};

// ===== API HELPER =====
async function apiCall(endpoint) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    const json = await res.json();
    if (!json.success) throw new Error(json.error);
    return json.data;
  } catch (err) {
    console.error('API Error:', err);
    return null;
  }
}

// 1. OMDb details - API keys backend එකේ
export async function getOMDbDetails(imdbId) {
  return await apiCall(`/omdb?i=${imdbId}`);
}

// 2. Video link එක ගන්න
export async function getVideoLink(imdbId, season = null, episode = null) {
  let url = `/video/${imdbId}`;
  if (season && episode) url += `?season=${season}&episode=${episode}`;
  return await apiCall(url);
}

// 3. Search කරන්න
export async function searchMovies(query) {
  return await apiCall(`/search?q=${encodeURIComponent(query)}`);
}

// 4. CineSubz movies ගන්න
export async function getMovies(page = 1) {
  return await apiCall(`/movies?page=${page}&per_page=20`);
}
