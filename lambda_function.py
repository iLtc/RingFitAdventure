import requests
import os
import pymongo
import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def lambda_handler(event, context):
    # Check Ring Fit Adventure inventory through PriceSpider
    r = requests.get('https://check.pricespider.com/?pmid=119478521,119837604,119837608,119837609')
    print(r.json())

    found = False

    for product in r.json()['productMatches']:
        if product['stockStatus'] != 0:
            found = True
            break


    # Connect to Database
    db_uri = os.environ.get('DATABASE_URI')

    client = pymongo.MongoClient(db_uri)

    db = client.get_default_database()


    # Record this checking

    history_collection = db.history

    history_collection.insert_one({'results': r.json(), 'time': datetime.datetime.now()})


    # Send Email if Found
    if found:
        message = Mail(
            from_email=os.environ.get('FROM_EMAIL'),
            to_emails=os.environ.get('TO_EMAIL'),
            subject='Ring Fit Adventure Found One!',
            html_content='Hello, I think I found a Ring Fit Adventure! Please visit https://www.nintendo.com/games/detail/ring-fit-adventure-switch/ to double check!')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)