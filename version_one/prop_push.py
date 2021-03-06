# Import dependencies 
import os, requests, json, time, datetime, sqlite3, smtplib
from config import key, host, email_user, email_pass, email_recipient

# Set email credentials
email_address = email_user
email_password = email_pass
recipient = email_recipient

# Set base URL and querystring for params
url = 'https://realtor.p.rapidapi.com/properties/list-for-sale'

querystring = {'city':'Austin',
               'offset':'0',
               'limit':'200',
               'state_code':'TX',
               'sort':'newest',
               'prop_type': 'multi_family',
               'is_pending': False,
               'is_contingent': False,
               'lot_sqft_min':'7405.2'
              }

headers = {
    'x-rapidapi-key': key,
    'x-rapidapi-host': host
    }

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
            listing['id'] = x['listing_id']
            listing['address'] = x['address']
            listing['listdate'] = x['list_date'][:10]
            listing['price'] = x['short_price']
            listing['url'] = x['rdc_web_url']
            new_listings.append(listing)
    return new_listings

def update(new_listings):
    '''Updates txt file of listings IDs; sends email for every new listing'''

    # Server set up for email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_address, email_pass)

    # Opens listing file
    with open('all_listings', 'r+') as f:
        listings_all = f.read().splitlines()

        # Checks if id already in file; appends if not
        for i in new_listings:
            if i['id'] not in listings_all:
                f.write(f"{i['id']}\n")
        
                # Composes email and sends
                subject = f"NEW MULTI-FAMILTY PROPERTY FOR SALE - {i['address']}"
                body = f"Address: {i['address']}\nList date: {i['listdate']}\nPrice: {i['price']}\nURL: {i['url']}"
                    
                msg = f'Subject: {subject}\n\n{body}'
                server.sendmail(email_address, recipient, msg)
    f.close()
    server.quit()

update(price_check(query()))


# def notify(new_listings):
#     '''Send ALL listings via email'''
#     num = 0
#     body = ''
#     ts = time.time()
#     timestamp = datetime.datetime.fromtimestamp(ts).strftime('%m/%d %H:%M')
#     subject = f'MULTI-FAMILTY PROPERTIES FOR SALE - {timestamp}'
#     for i in new_listings:
#         num += 1

#         body += f"{num}. Address: {i['address']}\nList date: {i['listdate']}\nPrice: {i['price']}\nURL: {i['url']}\n\n---------\n\n"
                    
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#     server.login(email_address, email_pass)

#     msg = f'Subject: {subject}\n\n{body}'
#     server.sendmail(email_address, recipient, msg)
#     server.quit()

# notify(price_check(query()))