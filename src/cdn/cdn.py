from flask import Flask, Response, abort, send_file, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv('APP_SECRET_KEY')
app.config['MONGO_URI'] = getenv('MONGO_URI')
client = MongoClient(getenv('MONGO_URI'))
users = client.linksbase.users
sysconf = client.linksbase['System configurations']

@app.route('/')
def index():
  return abort(404)

@app.route('/avatars/<username>')
def avatars(username):
  try:
    avatar = users.find_one({ 'username': username })['avatar']
    return Response(avatar.get('img'), mimetype=avatar.get('mimetype'))
  except AttributeError:
    return send_file('static/noavatar.png')
  except TypeError:
    return abort(404)

@app.route('/qrcodes/<username>')
def qrcodes(username):
  try:
    qrcode = users.find_one({ 'username': username })['qr_code']
    return Response(qrcode.get('img'), mimetype=qrcode.get('mimetype'))
  except:
    return abort(404)

@app.route('/media/<filename>')
def logo(filename):
  try:
    pictures = sysconf.find_one({
      'type': 'sc'
    })['pictures']

    for i in pictures:
      if filename == i['filename']:
        return Response(i.get('img'), mimetype=i.get('mimetype'))
    else:
      abort(404)
  except:
    return abort(404)

if __name__ == '__main__':
  app.run(port=9000)