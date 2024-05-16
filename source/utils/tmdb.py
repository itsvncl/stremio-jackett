import requests

from models.movie import Movie
from models.series import Series
from utils.logger import setup_logger

logger = setup_logger(__name__)


def replace_weird_characters(string):
    corresp = {
        'ā': 'a', 'ă': 'a', 'ą': 'a', 'ć': 'c', 'č': 'c', 'ç': 'c',
        'ĉ': 'c', 'ċ': 'c', 'ď': 'd', 'đ': 'd', 'è': 'e', 'é': 'e',
        'ê': 'e', 'ë': 'e', 'ē': 'e', 'ĕ': 'e', 'ę': 'e', 'ě': 'e',
        'ĝ': 'g', 'ğ': 'g', 'ġ': 'g', 'ģ': 'g', 'ĥ': 'h', 'î': 'i',
        'ï': 'i', 'ì': 'i', 'í': 'i', 'ī': 'i', 'ĩ': 'i', 'ĭ': 'i',
        'ı': 'i', 'ĵ': 'j', 'ķ': 'k', 'ĺ': 'l', 'ļ': 'l', 'ł': 'l',
        'ń': 'n', 'ň': 'n', 'ñ': 'n', 'ņ': 'n', 'ŉ': 'n', 'ó': 'o',
        'ô': 'o', 'õ': 'o', 'ö': 'o', 'ø': 'o', 'ō': 'o', 'ő': 'o',
        'œ': 'oe', 'ŕ': 'r', 'ř': 'r', 'ŗ': 'r', 'š': 's', 'ş': 's',
        'ś': 's', 'ș': 's', 'ß': 'ss', 'ť': 't', 'ţ': 't', 'ū': 'u',
        'ŭ': 'u', 'ũ': 'u', 'û': 'u', 'ü': 'u', 'ù': 'u', 'ú': 'u',
        'ų': 'u', 'ű': 'u', 'ŵ': 'w', 'ý': 'y', 'ÿ': 'y', 'ŷ': 'y',
        'ž': 'z', 'ż': 'z', 'ź': 'z', 'æ': 'ae', 'ǎ': 'a', 'ǧ': 'g',
        'ə': 'e', 'ƒ': 'f', 'ǐ': 'i', 'ǒ': 'o', 'ǔ': 'u', 'ǚ': 'u',
        'ǜ': 'u', 'ǹ': 'n', 'ǻ': 'a', 'ǽ': 'ae', 'ǿ': 'o', 'á': 'a',
    }

    for weird_char in corresp:
        string = string.replace(weird_char, corresp[weird_char])

    return string


def get_metadata(id, type, config):
    logger.info("Getting metadata for " + type + " with id " + id)

    language = "en" if "en" in config['languages'] else config['languages'][0]
    logger.info(f"Language set to: {language}")
    
    if id.startswith('tt'):
        result = get_metadata_with_imdb(type, id, config['tmdbApi'], language)
    else:
        result = get_metadata_with_tmdb(type, id, config['tmdbApi'], language)
        
    logger.info("Got metadata for " + type + " with id " + id)
    return result

def get_metadata_with_imdb(type, id, api_key, language):
    id_fragments = id.split(":")
    
    url = f"https://api.themoviedb.org/3/find/{id_fragments[0]}?api_key={api_key}&external_source=imdb_id&language={language}"
    response = requests.get(url)
    data = response.json()
    logger.info("Got response from TMDB")
    logger.info(data)

    if type == "movie":
        result = Movie(
            id=id,
            title=replace_weird_characters(data["movie_results"][0]["title"]),
            year=data["movie_results"][0]["release_date"][:4],
            language=language
        )
        return result
    else:
        result = Series(
            id=id,
            title=replace_weird_characters(data["tv_results"][0]["name"]),
            season="S{:02d}".format(int(id_fragments[1])),
            episode="E{:02d}".format(int(id_fragments[2])),
            language=language
        )
        return result

def get_metadata_with_tmdb(type, id, api_key, language):
    id_fragments = id.split(":")
    
    if type == "movie":
        url = f"https://api.themoviedb.org/3/movie/{id_fragments[1]}?api_key={api_key}&language={language}"
        response = requests.get(url)
        data = response.json()
        logger.info("Got response from TMDB with TMDB ID")
        logger.info(data)
        
        result = Movie(
            id=id,
            title=replace_weird_characters(data["title"]),
            year=data["release_date"][:4],
            language=language
        )
        
        return result
        
    else:
        url = f"https://api.themoviedb.org/3/tv/{id_fragments[1]}?api_key={api_key}&language={language}"
        response = requests.get(url)
        data = response.json()
        logger.info("Got response from TMDB with IMDB ID")
        logger.info(data)
        
        result = Series(
            id=id,
            title=replace_weird_characters(data["name"]),
            season="S{:02d}".format(int(id_fragments[2])),
            episode="E{:02d}".format(int(id_fragments[3])),
            language=language
        )
        return result
