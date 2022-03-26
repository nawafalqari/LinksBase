from requests import get

def encodeURL(url:str):
    url = url.replace('/', '%5C', len(url))
    
    return url

api_key = 'zl3lIGiFPLjj4BGXKtkX3tKa9u4IpkIc'
print(get(f'https://ipqualityscore.com/api/json/url/{api_key}/{encodeURL(input("> "))}').json()['unsafe'])