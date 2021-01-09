# Import dependencies 
import os, requests, json, time, datetime, sqlite3, smtplib
from config import key, host, email_user, email_pass, email_recipient
from properties import Listings

ts = time.time()

conn = sqlite3.connect('listings.db')
c = conn.cursor()

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
               'prop_type': 'multi_family'
              }

headers = {
    'x-rapidapi-key': key,
    'x-rapidapi-host': host
    }

# Create empty list for listings
all_listings = []
existing_listings = c.execute('SELECT address from Listings')
for x in existing_listings:
    all_listings.append(x)

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
            # if x['address'] not in existing_listings:
                # timestamp = datetime.datetime.fromtimestamp(ts).strftime('%m/%d %H:%M')
                # listing = Properties(timestamp, x['address'], x['short_price'], x['rdc_web_url'])
                # c.execute('INSERT INTO Properties VALUES ({}, {}, {}, {})'.format(listing.time_added, listing.address, listing.price, listing.url))
                # conn.commit()
            listing['time_added'] = datetime.datetime.fromtimestamp(ts).strftime('%m/%d %H:%M')
            listing['address'] = x['address']
            listing['price'] = x['short_price']
            listing['url'] = x['rdc_web_url']
            new_listings.append(listing)
    return new_listings


def update(new_listings):
    '''Updates db'''
    for i in new_listings:
        if i['address'] != existing_listings:
            # timestamp = datetime.datetime.fromtimestamp(ts).strftime('%m/%d %H:%M')
            # listing = Properties(timestamp, i['address'], i['price'], i['url'])
            print(i['address'])
            c.execute("INSERT INTO Listings VALUES (?,?,?)",(i['address'], i['price'], i['url']))

            conn.commit()

            subject = f"MULTI-FAMILTY PROPERTIES FOR SALE - {i['address']}"
            body += f"Address: {i['address']}\nPrice: {i['price']}\nURL: {i['url']}\n\n---------\n\n"
                    
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()

                smtp.login(email_address, email_password)

                msg = f'Subject: {subject}\n\n{body}'

                smtp.sendmail(email_address, email_address, msg)


# def list_check(new_listings):
#     '''Checks if new listing already in list, generates notification if not'''
#     for listing in new_listings:
#         if listing not in all_listings:
#             # listing = Listings(address=new_listings['address'], price=new_listings['price'], url=new_listings['url'])
#             # session.add(listing)
#             # session.commit()
#             all_listings.append(listing)
#             with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#                 smtp.ehlo()
#                 smtp.starttls()
#                 smtp.ehlo()

#                 smtp.login(email_address, email_password)

#                 subject = f"MULTI-FAMILTY PROPERTY FOR SALE: {listing['address']}"
#                 body = f"Address: {listing['address']}\n\nPrice: {listing['price']}\n\nURL: {listing['url']}"
#                 msg = f'Subject: {subject}\n\n{body}'

#                 smtp.sendmail(email_address, recipient, msg)

# def notify(new_listings):
#     '''Generates email notification'''
#     num = 0
#     subject = f"MULTI-FAMILTY PROPERTIES FOR SALE - {datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"
#     body = ''
#     for x in new_listings:
#         num += 1
#         body += f"{num}. Address: {x['address']}\nPrice: {x['price']}\nURL: {x['url']}\n\n---------\n\n"
        
#     with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
#         smtp.ehlo()
#         smtp.starttls()
#         smtp.ehlo()

#         smtp.login(email_address, email_password)

#         msg = f'Subject: {subject}\n\n{body}'

#         smtp.sendmail(email_address, email_address, msg)

ts = time.time()
update(price_check(query()))