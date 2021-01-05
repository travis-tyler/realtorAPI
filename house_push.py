# Import dependencies 
import requests
import json
import time
import os
import smtplib
from config import key, host, email_user, email_pass, email_recipient

email_address = email_user
email_password = email_pass
recipient = email_recipient

# Set base URL and querystring for params
url = 'https://realtor.p.rapidapi.com/properties/list-for-sale'

querystring = {'city':'Austin',
               'offset':'0',
               'limit':'200',
               'state_code':'TX',
               'sort':'relevance',
               'prop_type': 'multi_family',
               'postal_code':'78751'
              }

headers = {
    'x-rapidapi-key': key,
    'x-rapidapi-host': host
    }

# Create empty list for listings
all_listings = []

def query():
    '''Handles requests'''
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    return response

def price_check(response):
    '''Checks if listing under price cap and return summary'''
    new_listings = []
    for x in response['listings']:
        listing = {}
        if int(x['price_raw']) <= 699000:
            listing['address'] = x['address']
            listing['price'] = x['short_price']
            listing['url'] = x['rdc_web_url']
            new_listings.append(listing)
    return new_listings

def list_check(new_listings):
    '''Checks if new listing already in list, generates notification if not'''
    for listing in new_listings:
        if listing not in all_listings:
            all_listings.append(listing)
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(email_address, email_password)

                subject = f"MULTI-FAMILTY PROPERTY FOR SALE: {listing['address']}"
                body = f"Address: {listing['address']}\nPrice: {listing['price']}\nURL: {listing['url']}"
                msg = f'Subject: {subject}\n\n{body}'

                smtp.sendmail(email_address, recipient, msg)

list_check(price_check(query()))