from flask import Flask, jsonify, redirect, render_template, request, session
from pymongo import MongoClient
from dotenv import load_dotenv
from os import abort, getenv
from bcrypt import checkpw
import datetime
from json import loads, dumps
from requests import get

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv('APP_SECRET_KEY')
app.config['MONGO_URI'] = getenv('MONGO_URI')
client = MongoClient(getenv('MONGO_URI'))
users = client.linksbase.users
sysconf = client.linksbase['System configurations']


@app.route('/', methods=['GET', 'POST'])
def admin():
    if session.get('isLogged'):
        return redirect('control_panel')
    if request.method == 'POST':
        username = request.form.get('username').lower()
        password = request.form.get('password')

        user = sysconf.find_one({'username': username})

        if not user:
            return redirect('/')
        if checkpw(password.encode('utf-8'), user['password']):
            session['isLogged'] = True
            sysconf.update_one(user, {
                '$push': {
                    'control_panel_logs': {
                        'type': 'login to control panel',
                        'time': datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S %p'),
                        'remote_addr': request.environ.get('REMOTE_ADDR', None),
                        'HTTP_X_FORWARDED_FOR': request.environ.get('HTTP_X_FORWARDED_FOR', None)
                    }
                }
            })

            return redirect('control_panel')

    return '''
  <h2>Admin Control panel</h2>
  <form action="" method="POST">
    <input name="username" type="text" required autofocus>
    <input type="password" name="password" required>
    <input type="submit" value="login">
  </form>
  '''


@app.route('/control_panel', methods=['GET', 'POST'])
def control_panel():
    if not session.get('isLogged'):
        return redirect('/')
    if request.method == 'POST':
        image = request.files.get('image')
        filename = request.form.get('filename')

        image_binary_data = image.stream.read()
        image_mimetype = image.mimetype

        sysconf.update_one({'type': 'sc'}, {
            '$push': {
                'pictures': {
                    'img': image_binary_data,
                    'mimetype': image_mimetype,
                    'filename': filename
                }
            }
        })
    return render_template('control_panel.html')

@app.route('/remove_user', methods=['GET', 'POST'])
def remove_user_panel():
    if request.method == 'GET':
        return redirect('/')

    username = request.form.get('username')
    u = users.find_one({'username': username})

    if not u:
        return 'Invalid Username'
    users.delete_one(u)

    return redirect('/')

@app.route('/remove_user/<user>', methods=['GET', 'POST'])
def remove_user(user):
    if request.method == 'GET':
        return redirect('/')
    u = users.find_one({'username': user})

    if not u:
        return 'Invalid Username'
    users.delete_one(u)

    return redirect('/')

@app.route('/verify_user', methods=['GET', 'POST'])
def verify_user_panel():
    if request.method == 'GET':
        return redirect('/')
    
    username = request.form.get('username')
    u = users.find_one({'username': username})

    if not u:
        return 'Invalid Username'
    users.update_one({'username': username}, {
        '$set': {
            'isVerified': True
        }
    })

    return redirect('/')

@app.route('/unverify_user', methods=['GET', 'POST'])
def unverify_user_panel():
    if request.method == 'GET':
        return redirect('/')
    
    username = request.form.get('username')
    u = users.find_one({'username': username})

    if not u:
        return 'Invalid Username'
    users.update_one({'username': username}, {
        '$unset': {
            'isVerified': True
        }
    })

    return redirect('/')

@app.route('/set_evexsland_staff_user', methods=['GET', 'POST'])
def set_evexsland_staff_user():
    if request.method == 'GET':
        return redirect('/')
    
    username = request.form.get('username')
    u = users.find_one({'username': username})

    if not u:
        return 'Invaild Username'
    users.update_one({'username': username}, {
        '$set': {
            'isEvexsLandStaff': True
        }
    })

    return redirect('/')

@app.route('/unset_evexsland_staff_user', methods=['GET', 'POST'])
def unset_evexsland_staff_user():
    if request.method == 'GET':
        return redirect('/')
    
    username = request.form.get('username')
    u = users.find_one({'username': username})
    
    if not u:
        return redirect('/')
    users.update_one({'username': username}, {
        '$unset': {
            'isEvexsLandStaff': True
        }
    })

    return redirect('/')

@app.route('/api/repeated_users/<user>')
def api_repeated_users(user):
    us = list(users.find({'username': user}))

    for i in us:
        i['_id'] = str(i['_id'])
        del i['password']
        del i['avatar']
        del i['qr_code']

    print(type(us))

    if len(us) == 1:
        return jsonify({
            '_error': True,
        })

    return jsonify(dumps(us))


@app.route('/logout')
def admin_logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000)