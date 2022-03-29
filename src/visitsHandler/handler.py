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

with open('data.json', 'r') as dataFile:
    data = load(dataFile)

def weekly_handler():
    all_users = users.find({})

    for user in all_users:
        print(user['username'])
        # this will create "monthly_visits" and "weekly_visits" for every user that doesn't have
        if (not user.get('monthly_visits')) and (not user.get('monthly_visits')):
            today = datetime.datetime.now()
            daysRange = list(calendar.monthrange(today.year, today.month))
            weekStart = today - datetime.timedelta(days=today.weekday())
            weekEnd = weekStart + datetime.timedelta(days=6)

            weekStart = weekStart.strftime('%m-%d-%Y')
            weekEnd = weekEnd.strftime('%m-%d-%Y')

            daysRange[-1] += 1

            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

            week = {
                f'{w}': {
                    'date': f'{w}',
                    'visits': 0
                } for w in weekdays
            }

            week['week_start'] = weekStart
            week['week_end'] = weekEnd

            users.update_one(user, {
                '$set': {
                    'visits_weekly': week
                }
            })

        # This will get this week's data and store it in "data.json"
        today = datetime.datetime.now()

        weekly_data = user.get('visits_weekly')

        weekStart = today - datetime.timedelta(days=today.weekday())
        weekEnd = weekStart + datetime.timedelta(days=6)

        weekStart = weekStart.strftime('%m-%d-%Y')
        weekEnd = weekEnd.strftime('%m-%d-%Y')

        weekStartToWeekEnd = f'{weekStart}--{weekEnd}'

        if not data.get(user.get('username')):
            data[user.get('username')] = {
                'weekly_data': {
                    weekStartToWeekEnd: weekly_data
                }
            }
        
        else:
            data[user.get('username')]['weekly_data'] = {
                weekStartToWeekEnd: weekly_data
            }

        with open('data.json', 'w') as dataFile:
            dump(data, dataFile, indent=3)

        today = datetime.datetime.now()
        daysRange = list(calendar.monthrange(today.year, today.month))

        daysRange[-1] += 1

        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        week = {
            f'{w}': {
                'date': f'{w}',
                'visits': 0
            } for w in weekdays
        }

        week['week_start'] = weekStart
        week['week_end'] = weekEnd

        users.update_one(user, {
            '$set': {
                'visits_weekly': week
            }
        })
        print('-----------------------------------------------------------')
        print(f'Updated weekly job for this week. {weekStartToWeekEnd}')
        print('-----------------------------------------------------------')

def monthly_handler():
    all_users = users.find({})

    for user in all_users:
        # this will create "monthly_visits" and "weekly_visits" for every user that doesn't have
        if (not user.get('monthly_visits')) and (not user.get('monthly_visits')):
            today = datetime.datetime.now()
            daysRange = list(calendar.monthrange(today.year, today.month))

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

            users.update_one(user, {
                '$set': {
                    'visits_monthly': _30_days,
                }
            })

        # This will get this week's data and store it in "data.json"
        today = datetime.datetime.now()

        monthly_data = user.get('visits_monthly')

        monthStart = _30_days[list(_30_days)[0]]['date']
        monthEnd = _30_days[list(_30_days)[-1]]['date']

        monthStartToMonthEnd = f'{monthStart}--{monthEnd}'

        if not data.get(user.get('username')):
            data[user.get('username')] = {
                'monthly_data': {
                    monthStartToMonthEnd: monthly_data
                }
            }
        
        else:
            data[user.get('username')]['monthly_data'] = {
                monthStartToMonthEnd: monthly_data
            }

        with open('data.json', 'w') as dataFile:
            dump(data, dataFile, indent=3)
        print('-----------------------------------------------------------')
        print(f'Updated monthly job for this month. {monthStartToMonthEnd}')
        print('-----------------------------------------------------------')
        print('\n')
        
schedule.every().monday.at('00:00').do(weekly_handler)

while True:
    schedule.run_pending()
    time.sleep(1)