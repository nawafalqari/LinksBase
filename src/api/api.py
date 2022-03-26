from flask import Flask, request, jsonify
from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv('APP_SECRET_KEY')

client = MongoClient(getenv('MONGO_URI'))
users = client.linksbase.users

@app.route('/')
def index():
    return 'LinksBase API'

@app.route('/user/')
def user():
    return jsonify({
        'path': request.path,
        '_error': True,
        '_error_message': 'No user provided'
    })

@app.route('/user/<username>/')
def user_data(username):
    u = users.find_one({'username': username})
    if not u:
        return jsonify({
            '_error': True,
            '_error_message': f'User {username} not found'
        })
    del u['password']
    del u['email']
    del u['_id']
    del u['visits_monthly']
    del u['visits_weekly']
    u['avatar'] = f'https://cdn.linksb.me/avatars/{username}'
    u['qr_code'] = f'https://cdn.linksb.me/qrcodes/{username}'
    return jsonify({
        '_error': False,
        '_error_message': '',
        **u
    })

@app.route('/qrcode/')
def qrcode():
    return jsonify({
        'path': request.path,
        '_error': True,
        '_error_message': 'No user provided'
    })

@app.route('/qrcode/<username>/')
def qrcode_data(username):
    u = users.find_one({'username': username})
    if not u:
        return jsonify({
            '_error': True,
            '_error_message': f'User {username} not found'
        })

    d = {}
    d['qr_code'] = f'https://cdn.linksb.me/qrcodes/{username}'
    return jsonify({
        '_error': False,
        '_error_message': '',
        **d
    })

@app.route('/avatar/')
def avatar():
    return jsonify({
        'path': request.path,
        '_error': True,
        '_error_message': 'No user provided'
    })

@app.route('/avatar/<username>/')
def avatar_data(username):
    u = users.find_one({'username': username})
    if not u:
        return jsonify({
            '_error': True,
            '_error_message': f'User {username} not found'
        })
    del u['password']
    del u['email']
    del u['_id']
    del u['qr_code']
    del u['data']
    del u['registered_in']
    u['avatar'] = f'https://cdn.linksb.me/avatars/{username}'
    return jsonify({
        '_error': False,
        '_error_message': '',
        **u
    })

if __name__ == '__main__':
    app.run(port=9090, debug=True)