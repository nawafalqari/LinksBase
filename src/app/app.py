from flask import Flask, render_template, url_for, request, redirect, session, abort
from flask_pymongo import PyMongo
from random import sample
from pymongo import MongoClient
from bcrypt import hashpw, checkpw, gensalt
import validators
import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from PIL import Image
import qrcode
from mimetypes import MimeTypes
import calendar
from time import time
from threading import Thread
from time import sleep
from collections import OrderedDict

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET_KEY')
app.config['MONGO_URI'] = os.getenv('MONGO_URI')

images_client = PyMongo(app)

mongodb_connection_url = os.getenv('MONGO_URI')
client = MongoClient(mongodb_connection_url)
users = client.linksbase.users
sysconf = client.linksbase['System configurations']

# def gen_code():
#     numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
#                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
#     code = sample(numbers, 18)
#     codes = sysconf.find_one({
#         '_id': ObjectId('62016109f996a323ddddeda3'),
#         'type': 'sc'
#     })['avatar_ids']
#     if code in codes:
#         gen_code()
#     return ''.join(code)

def normal_gen_code():
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9',
               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    code = sample(numbers, 20)
    return ''.join(code)


def has_symbols(s):
    return (True if True in list(map(lambda e: False if e.isnumeric() or e.isalpha() else True, list(s))) else False)


def is_english(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def clean_discover_data(data):
    d = data.copy()
    for i in d:
        del i['password']
        del i['qr_code']
        del i['avatar']
        i['description'] = i['data']['description']
        i['url'] = i['data']['url']
        del i['data']

    nd = []

    for i in range(0, len(d), 3):
        nd.append(d[i:i+3])

    # mid = len(d) // 2
    # l1 = d[0:mid]
    # l2 = d[mid:]
    # nd = [l1, l2]

    return nd

def get_day_index(l:list, day):
    for i in range(0, len(l)):
        if l[i][0] == day:
            return i

def increment_visits(username):
    '''

    Visits structer

    ```py
    [
        [ "12-3-2022", 8 ],
        [ "13-3-2022", 15 ],
        [ "14-3-2022", 2 ],
        [ "15-3-2022", 35 ],
    ]
    ```

    date behavior

    ```py
    datetime.now().strftime('%m-%d-%Y')
    ```

    '''
    u = users.find_one({'username': username})
    today = datetime.datetime.now()
    weekDayName = f'{datetime.datetime.now().strftime("%A")}'
    
    if not u:
        return False
    if (not u.get('visits_monthly')) and (not u.get('visits_weekly')):
        todaysFormat = f'{today.month}-{today.day}-{today.year}'
        daysRange = list(calendar.monthrange(today.year, today.month))
        t = today.strptime(todaysFormat, '%m-%d-%Y')

        weekStart = t - datetime.timedelta(days=t.weekday())
        weekEnd = weekStart + datetime.timedelta(days=6)

        weekStart = weekStart.strftime('%m-%d-%Y')
        weekEnd = weekEnd.strftime('%m-%d-%Y')

        daysRange[-1] += 1

        _30_days = {
            f'{d}': {
                'date': f'{today.month}-{d}-{today.year}',
                'visits': 0
            }
        for d in range(*daysRange) }
        monthStart = _30_days[list(_30_days)[0]]['date']
        monthEnd = _30_days[list(_30_days)[-1]]['date']
        _30_days['month_start'] = monthStart
        _30_days['month_end'] = monthEnd

        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        week = {
            f'{w}': {
                'date': f'{w}',
                'visits': 0
            } for w in weekdays
        }
        week['week_start'] = weekStart
        week['week_end'] = weekEnd

        users.update_one({'username': username}, {
            '$set': {
                'visits_monthly': _30_days,
                'visits_weekly': week
            }
        })

        users.update_one({'username': username}, { '$inc': {
                f'visits_monthly.{today.day}.visits': 1
            } 
        })

        users.update_one({'username': username}, {
            '$inc': {
                f'visits_weekly.{weekDayName}.visits': 1
            }
        })
        return True

    users.update_one({'username': username}, { '$inc': {
            f'visits_monthly.{today.day}.visits': 1
        } 
    })

    users.update_one({'username': username}, {
        '$inc': {
            f'visits_weekly.{weekDayName}.visits': 1
        }
    })
    return True

# today = datetime.datetime.now()
# todaysFormat = [f'{today.month}-{today.day}-{today.year}']
# daysRange = list(calendar.monthrange(today.year, today.month))

# daysRange[-1] += 1

# listt = [
#     [f'{today.month}-{d}-{today.year}', 0] for d in range(*daysRange)
# ]

# index = get_day_index(listt, '3-30-2022')

# print(index)
# print(listt[index])

@app.route('/', methods=['GET', 'POST'])
def index():
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')

    if request.args.get('msg') and request.args.get('msg_type') and request.args.get('route') == 'save_custom_theme' and session.get('isLogged'):
        user = users.find_one({'username': session.get('username')})
        session['data'] = user['data']
        return render_template('logged_in.html',
        msg=request.args.get('msg'),
        msg_type=request.args.get('msg_type'),
        main_color= user.get('main_color'),
        background_color=user.get('background_color'),
        text_color=user.get('text_color'),
        session=session)
    if request.args.get('msg') and request.args.get('msg_type') and session.get('isLogged'):
        user = users.find_one({'username': session.get('username')})
        session['data'] = user['data']
        return render_template('logged_in.html', msg=request.args.get('msg'), msg_type=request.args.get('msg_type'), session=session)

    # SAVE DATA

    if (request.method == 'POST' and session.get('isLogged') == True):
        description = request.form.get('description')

        avatar = request.files.get('avatar')
        youtube = request.form.get('youtube')
        twitter = request.form.get('twitter')
        instagram = request.form.get('instagram')
        tiktok = request.form.get('tiktok')
        twitch = request.form.get('twitch')
        other = request.form.get('other')
        theme = request.form.get('theme')

        user = users.find_one({'username': session.get('username')})

        if avatar:
            fn = secure_filename(avatar.filename)
            extensions = ['png', 'jpg', 'jpeg']
            avatar_extension = fn.split('.')[-1]

            if user.get('isDonator') == True:
                extensions.append('gif')
                session['isDonator'] = True

            if (not session.get('isDonator')) and (avatar_extension == 'gif'):
                return render_template('logged_in.html',
                                       session=session,
                                       msg='Animated avatars are just for patreon donators',
                                       msg_type='danger',
                                       dc=description,
                                       yt=youtube,
                                       tt=twitter,
                                       ig=instagram,
                                       tk=tiktok,
                                       ttv=twitch,
                                       ot=other)

            if avatar_extension not in extensions:
                return render_template('logged_in.html',
                                       session=session,
                                       msg='Invalid file extension',
                                       msg_type='danger',
                                       dc=description,
                                       yt=youtube,
                                       tt=twitter,
                                       ig=instagram,
                                       tk=tiktok,
                                       ttv=twitch,
                                       ot=other)

            users.update_one(user, {
                '$set': {'avatar': {
                    'img': avatar.stream.read(),
                    'mimetype': avatar.mimetype,
                    'filename': fn
                }}
            })

        if (not validators.url(youtube) and (youtube != 'https://' and youtube != '')) or \
            (not validators.url(twitter) and (twitter != 'https://' and twitter != '')) or \
            (not validators.url(instagram) and (instagram != 'https://' and instagram != '')) or \
            (not validators.url(tiktok) and (tiktok != 'https://' and tiktok != '')) or \
            (not validators.url(twitch) and (twitch != 'https://' and twitch != '')) or \
                (not validators.url(other) and (other != 'https://' and other != '')):
            return render_template('logged_in.html',
                                   session=session,
                                   msg='Something went wrong, make sure every url is right!',
                                   msg_type='danger',
                                   dc=description,
                                   yt=youtube,
                                   tt=twitter,
                                   ig=instagram,
                                   tk=tiktok,
                                   ttv=twitch,
                                   ot=other)
        
        user = users.find_one({'username': session.get('username')})

        users.update_one(user, {
            '$set': {
                'data': {
                    'url': user['data']['url'],
                    'description': description,
                    'theme': theme,
                    'youtube': youtube,
                    'twitter': twitter,
                    'instagram': instagram,
                    'tiktok': tiktok,
                    'twitch': twitch,
                    'other': other,
                }
            }
        })

        user = users.find_one({'username': session.get('username')})
        session['data'] = user['data']
        if isinstance(user['avatar'], dict):
            session['isAvatar'] = True
        else:
            session['isAvatar'] = False

        if user.get('isDonator') == True:
            session['isDonator'] = True

        if user.get('isDonator') == True:
            return render_template('logged_in.html', 
            session=session,
            msg='Changes are saved!',
            msg_type='success',
            main_color= user.get('main_color'),
            background_color=user.get('background_color'),
            text_color=user.get('text_color'))

        return render_template('logged_in.html',
        session=session,
        msg='Changes are saved!',
        msg_type='success',
        main_color= user.get('main_color'),
        background_color=user.get('background_color'),
        text_color=user.get('text_color'))

    if session.get('isLogged'):
        user = users.find_one({'username': session.get('username')})
        session['data'] = user['data']
        if isinstance(user['avatar'], dict):
            session['isAvatar'] = True
        else:
            session['isAvatar'] = False

        if user.get('isDonator') == True:
            session['isDonator'] = True

        return render_template('logged_in.html',
        session=session,
        main_color= user.get('main_color'),
        background_color=user.get('background_color'),
        text_color=user.get('text_color'))

    # return redirect('login')
    return render_template('not_logged_in.html')

@app.route('/save_custom_theme', methods=['GET', 'POST'])
def save_custom_theme():
    if request.method == 'GET':
        return redirect('/')
    if not session.get('isLogged'):
        return redirect('/')
    
    u = users.find_one({'username': session.get('username')})
    if not u.get('isDonator') == True:
        return redirect(url_for('index', msg='Custom themes are only for donators', msg_type='danger'))

    main_color = request.form.get('main_color')
    background_color = request.form.get('background_color')
    text_color = request.form.get('text_color')

    users.update_one({'username': session.get('username')}, {
        '$set': {
            'main_color': main_color,
            'background_color': background_color,
            'text_color': text_color
        }
    })

    return redirect(url_for('index',
    route='save_custom_theme',
    msg='Custom theme was saved, note: You need to set the theme to "custom theme"',
    msg_type='success'))

@app.route('/show_theme/<theme>/<username>')
def save_theme(theme, username):
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')
    
    u = users.find_one({'username': username})

    if not u:
        return abort(404)

    hasAvatar = False
    if not (u.get('avatar') == 'noavatar.png'):
        hasAvatar = True

    udata = {
        'username': u['username'],
        'description': u['data']['description'],
        'avatar': f'{session["config"]["cdn_url"]}/avatars/{u["username"]}',
        'registered_in': u['registered_in'],
        'data': u['data'],
        'hasAvatar': hasAvatar,
    }

    if u.get('isVerified') == True:
        udata['isVerified'] = True
    if u.get('isDonator') == True:
        udata['isDonator'] = True
    
    return render_template(f'themes/{theme}.html', session=session, udata=udata)

@app.route('/register', methods=['GET', 'POST'])
def register():
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')
    if session.get('isLogged') == True:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email').strip()
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')
        registration_date = datetime.datetime.now().strftime('%m/%d/%Y, %H:%M:%S %p')
        user_url = f'{request.root_url}{username}'

        numbers = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')

        illigal_usernames = [
            'login',
            'register',
            'logout',
            'discover',
            'tos',
            'termsofservice',
            'statics'
        ]

        if users.count_documents({'email': email}) != 0:
            return render_template('register.html', msg='There is Another account with the same email, Use different one', msg_type='danger', email=email, username=username)
        if not validators.email(email):
            return render_template('register.html', msg='Invalid email', msg_type='danger', email=email, username=username)
        if users.count_documents({'username': username}) != 0:
            return render_template('register.html', msg='Username Already used, Try another one', msg_type='danger', email=email, username=username)
        if username.startswith(numbers):
            return render_template('register.html', msg='Username can\'t start with number', msg_type='danger', email=email, username=username)
        if len(username) < 3:
            return render_template('register.html', msg='Very short username', msg_type='danger', email=email, username=username)
        if has_symbols(username) or not is_english(username):
            return render_template('register.html', msg='You can\'t use special characters in username', msg_type='danger', email=email, username=username)
        if len(password) < 6:
            return render_template('register.html', msg='Week password', msg_type='danger', email=email, username=username)
        if username in illigal_usernames:
            return render_template('register.html', msg=f'Username "{username}" is unavailable.', msg_type='danger', email=email, username=username)
        else:
            logo = Image.open('static/images/qrcode_logo.png')

            qr_big = qrcode.QRCode(version=1, error_correction=qrcode.ERROR_CORRECT_H, border=1, box_size=60)

            qr_big.add_data(user_url)
            qr_big.make()
            img_qr_big = qr_big.make_image(fill_color='black', back_color='white')

            pos = ((img_qr_big.size[0] - logo.size[0]) // 2, (img_qr_big.size[1] - logo.size[1]) // 2)

            img_qr_big.paste(logo, pos, mask=logo)

            filename = f'{normal_gen_code()}.png'

            img_qr_big.save(filename)

            with open(filename, 'rb') as qrcode_file:
                qrcode_binary = qrcode_file.read()
                mimetype = MimeTypes().guess_type(filename)[0]

            if os.path.exists(filename):
                os.remove(filename)

            sysconf.update_one({
                'type': 'sc'
            },
                {
                '$push': {
                    'usernames': username
                }
            }
            )

            epassword = hashpw(password.encode('utf-8'), gensalt())
            users.insert_one({'email': email,
                              'username': username,
                              'password': epassword,
                              'registered_in': registration_date,
                              'avatar': 'noavatar.png',
                              'qr_code': {
                                  'img': qrcode_binary,
                                  'mimetype': mimetype,
                                  'filename': f'{username}_qr.png'
                              },
                              'data': {
                                  'url': user_url,
                                  'description': 'Hey there, I use linksbase',
                                  'theme': 'linksbase',
                                  'youtube': '',
                                  'twitter': '',
                                  'instagram': '',
                                  'tikTok': '',
                                  'twitch': '',
                                  'other': ''
                              }})

            return redirect(url_for('login', msg='You have signed up successfully', msg_type='success'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')
    if request.args.get('msg') and request.args.get('msg_type'):
        return render_template('login.html', msg=request.args.get('msg'), msg_type=request.args.get('msg_type'))
    if session.get('isLogged') == True:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')

        user = users.find_one({ 'username': username })

        if not user:
            return render_template('login.html', msg='Invalid username or password', msg_type='danger', username=username)
        if checkpw(password.encode('utf-8'), user['password']):
            session['isLogged'] = True
            session['username'] = username
            session['email'] = user['email']
            session['data'] = user['data']

            if user.get('isDonator') == True:
                session['isDonator'] = True

            if isinstance(user['avatar'], dict):
                session['isAvatar'] = True
            else:
                session['isAvatar'] = False

            return redirect(url_for('index'))
        else:
            return render_template('login.html', msg='Invalid username or password', msg_type='danger', username=username)
    return render_template('login.html')


@app.route('/logout')
def logout():
    if session.get('isLogged') == True:
        session.clear()
        session['config'] = {}
        session['config']['cdn_url'] = os.getenv('CDN_URL')
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/discover')
def discover():
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')

    users_length = users.count_documents({})
    wanted_number_of_users = users_length
    users_data = list(reversed(list(users.find({}, skip=(users_length - wanted_number_of_users)))))
    cleaned_data = clean_discover_data(users_data)

    verified_users = clean_discover_data(list(users.find({'isVerified': True})))

    donators = clean_discover_data(list(users.find({'isDonator': True})))

    return render_template('discover.html', users_data=cleaned_data, verified_users=verified_users, donators=donators, session=session)

@app.route('/tos')
def tos():
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')
    return 'Terms Of Services'

@app.route('/termsofservices')
def termsofservices():
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')
    return 'Terms Of Services'

@app.route('/statics')
def statics():
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')

    if not session.get('isLogged'):
        return redirect(url_for('index'))

    u = users.find_one({ 'username': session.get('username') })
    visits_monthly = u.get('visits_monthly')
    visits_weekly = u.get('visits_weekly')

    if not visits_monthly or not visits_weekly:
        increment_visits(session.get('username'))
        u = users.find_one({ 'username': session.get('username') })
        visits_monthly = u.get('visits_monthly')
        visits_weekly = u.get('visits_weekly')
    
    if visits_monthly.get('month_start'):
        del visits_monthly['month_start']
    if visits_monthly.get('month_end'):
        del visits_monthly['month_end']

    if visits_weekly.get('week_start'):
        del visits_weekly['week_start']
    if visits_weekly.get('week_end'):
        del visits_weekly['week_end']

    monthly_labels = [visits_monthly[row]['date'] for row in visits_monthly]
    monthly_values = [visits_monthly[row]['visits'] for row in visits_monthly]

    weekly_labels = [visits_weekly[row]['date'] for row in visits_weekly]
    weekly_values = [visits_weekly[row]['visits'] for row in visits_weekly]
    
    return render_template('statics.html',
    monthly_labels=monthly_labels,
    monthly_values=monthly_values,
    weekly_labels=weekly_labels,
    weekly_values=weekly_values,
    session=session)

@app.route('/<username>')
def user(username):
    session['config'] = {}
    session['config']['cdn_url'] = os.getenv('CDN_URL')

    u = users.find_one({'username': username})

    if not u:
        return abort(404)

    hasAvatar = False
    if not (u.get('avatar') == 'noavatar.png'):
        hasAvatar = True

    udata = {
        'username': u['username'],
        'description': u['data']['description'],
        'avatar': f'{session["config"]["cdn_url"]}/avatars/{u["username"]}',
        'registered_in': u['registered_in'],
        'data': u['data'],
        'hasAvatar': hasAvatar,
    }

    if u.get('isVerified') == True:
        udata['isVerified'] = True
    if u.get('isDonator') == True:
        udata['isDonator'] = True
    if u.get('isEvexsLandStaff') == True:
        udata['isEvexsLandStaff'] = True

    increment_visits(username)

    if u['data']['theme'] == 'custom':
        return render_template('themes/custom_theme.html',
        session=session,
        udata=udata,
        main_color=u.get('main_color'),
        background_color=u.get('background_color'),
        text_color=u.get('text_color'))
    if u['data']['theme'] == 'linksbase':
        return render_template('themes/linksbase_main_theme.html', session=session, udata=udata)
    if u['data']['theme'] == 'light':
        return render_template('themes/light_theme.html', session=session, udata=udata)
    if u['data']['theme'] == 'green':
        return render_template('themes/green_theme.html', session=session, udata=udata)
    if u['data']['theme'] == 'orange':
        return render_template('themes/orange_theme.html', session=session, udata=udata)
    if u['data']['theme'] == 'blue':
        return render_template('themes/blue_theme.html', session=session, udata=udata)
    if u['data']['theme'] == 'red':
        return render_template('themes/red_theme.html', session=session, udata=udata)
    if u['data']['theme'] == 'dark_blue':
        return render_template('themes/dark_blue_theme.html', session=session, udata=udata)

    # account does not exist
    return abort(404)

if __name__ == '__main__':
    app.run(debug=True)