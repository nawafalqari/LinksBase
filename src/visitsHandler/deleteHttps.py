import datetime
from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
import calendar
from json import load, dump
from keepalive import run_server 
import datetime
import calendar
from threading import Thread
import schedule
import time

load_dotenv()

client = MongoClient(getenv('MONGO_URI'))
users = client.linksbase.users
test = client.linksbase.test

def deleteHttpsFromEveryUser():
    all_users = users.find({})

    for user in all_users:
        user_data = user['data'].copy()

        for key, val in user_data.items():
            if (key == 'url') or (key == 'description') or (key == 'theme'):
                continue
            if (val == 'https://') or (val == 'http://'):
                user_data[key] = ''
        else:
            users.update_one(user, {
                '$set': {
                    'data': user_data
                }
            })

        print('--------------------------------------')
        print(f'Updated udata for {user["username"]}')
        print('--------------------------------------')

deleteHttpsFromEveryUser()