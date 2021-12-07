# Stock Trading News Alert

#########################
# Created by 4bd3ss4m4d #
#########################

# Importing Modules & Libraries
import os
import requests
import smtplib
import time

# ---------------------------- CONSTANTS ------------------------------- #

# ------- Maximum growth rate ------- #
MAX_INCREASE_RATE = 5
MAX_DECREASE_RATE = -5

# ------- Waiting Time ------- #
WAITING_TIME = 10

# ------- Alpha Vantage API Parameters & End point------- #

# Alpha Vantage API Key from https://www.alphavantage.co/
ALPHA_VANTAGE_API_KEY = 'INSERT ALPHA VANTAGE API KEY'

# Alpha Vantage's 'Intraday History DATA' End Point Parameters
ALPHA_VANTAGE_API_FUNCTION = 'TIME_SERIES_INTRADAY'
ALPHA_VANTAGE_DATA_INTERVAL = '60min'

# Alpha Vantage End Point
ALPHA_VANTAGE_ENDPOINT = 'https://www.alphavantage.co/query'

# ------- Stock News API Parameters & End point------- #

# News API KEY from https://newsapi.org/
NEWS_API_KEY = 'INSERT NEWS API KEY'

# News API End point
NEWS_API_ENDPOINT = 'https://newsapi.org/v2/everything'

MAX_ARTICLES_NUM = 5

# ------- Maximum growth rate ------- #

# My Account Credentials
MY_EMAIL = os.environ.get('GMAIL_USER')
MY_PASSWORD = os.environ.get('GMAIL_PASSWORD')
# Recipient Email
RECIPIENT_EMAILS = ['abd3ss4m4d@gmail.com', 'abdessamad.login@gmail.com']


# ---------------------------- Get Stock Data ------------------------------- #
def get_stock_data(stock_symbol_wanted):
    # Alpha Vantage's 'Intraday History DATA' End Point Parameters
    parameters = {'function': ALPHA_VANTAGE_API_FUNCTION,
                  'symbol': stock_symbol_wanted,
                  'interval': '60min',
                  'apikey': ALPHA_VANTAGE_API_KEY}

    # Send HTTP request to Alpha vantage API
    request = requests.get(ALPHA_VANTAGE_ENDPOINT, params=parameters)

    # Raise an exception if something goes wrong
    request.raise_for_status()

    # Get and return raw json data from API
    return request.json()


# ---------------------------- Calculate growth rate ------------------------------- #
def calc_growth_rate(raw_json_data):

    # Last Refreshed Data
    fetching_data_time = raw_json_data['Meta Data']['3. Last Refreshed']

    # Get opening stock price
    opening_stock_price = float(raw_json_data['Time Series (60min)'][fetching_data_time]['1. open'])

    # Get closing stock price
    closing_stock_price = float(raw_json_data['Time Series (60min)'][fetching_data_time]['4. close'])

    # Calculate the growth rate of the closing stock
    growth_rate = ((closing_stock_price - opening_stock_price) / opening_stock_price) * 100

    return growth_rate


# ---------------------------- Get relevant News ------------------------------- #
def get_stock_news(stock_info):
    # Stock News API Parameters
    parameters = {'apiKey': NEWS_API_KEY,
                  'qInTitle': stock_info['Stock name'],
                  'language': 'en',
                  'sortBy': 'relevancy'
                  }

    # Send HTTP request to News API
    request = requests.get(NEWS_API_ENDPOINT, params=parameters)

    # Raise an exception if something goes wrong
    request.raise_for_status()

    # Get raw news data
    raw_news_data = request.json()

    # Get articles
    articles = raw_news_data['articles']

    # Get first 5 articles from raw news data if the total results is more or equals to 5
    news_total_results = raw_news_data['totalResults']

    # Return only 5 articles if the total news results is greater or equals 5
    if news_total_results >= MAX_ARTICLES_NUM:
        return articles[:MAX_ARTICLES_NUM]
    else:
        return articles


# ---------------------------- Create message body ------------------------------- #
def create_message_body(raw_articles):
    # Create a text file
    message_body = f''

    # Append article infos to the message body
    for article in raw_articles:
        message_body += '\n'
        message_body += f"\nTitle: {article['title']}\n"
        message_body += f"\nBrief Description: \n{article['description']}\n"
        message_body += f"\nFor more details visit the following url: {article['url']}\n"
        message_body += f"\n_______________________________________"
    message_body += '\n Message sent by Stock Trading Alert Program'

    return message_body


# ---------------------------- SMTP Sender ------------------------------- #
def send_mail(message_subject, message_body):

    # Send Mail for each mail in the recipient emails
    for recipient_email in RECIPIENT_EMAILS:
        # Open an SMTP connexion using the default mail submission port using 587
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            message_body.encode('utf-8')
            # command sent by an email server to identify itself when connecting to another email server to start the
            # process of sending an email.
            smtp.ehlo()
            # StartTLS is a protocol command used to inform the email server that the email client wants to upgrade
            # from an insecure connection to a secure one using TLS
            smtp.starttls()
            # Rerun ehlo to reidentify ourselves as an encrypted connexion
            smtp.ehlo()
            # Login
            smtp.login(user=MY_EMAIL, password=MY_PASSWORD)
            # Message to send
            message = f'Subject: {message_subject}\n\n{message_body}'
            # Sending the Message
            smtp.sendmail(from_addr=MY_EMAIL, to_addrs=recipient_email, msg=message.encode("utf8"))
            # Print Sent Successfully
            print(f'Mail was successfully sent to {recipient_email}')


# ---------------------------- Main Function------------------------------- #
def main():
    # Name of the Stock name
    stocks_list = [{"Stock name": "Tesla", "Stock symbol": "TSLA"},
                   {"Stock name": "Apple", "Stock symbol": "AAPL"},
                   {"Stock name": "Alphabet", "Stock symbol": "GOOG"},
                   {"Stock name": "Facebook", "Stock symbol": "FB"}
                   ]
    again = 'y'
    while again == 'y':
        for stock in stocks_list:

            # Get the Stock's data
            stock_data = get_stock_data(stock["Stock symbol"])

            # Calculate Growth Rate of Stock
            growth_rate = calc_growth_rate(stock_data)

            # Check if growth rate is greater or equals to MAX_GROWTH_RATE
            if growth_rate >= MAX_INCREASE_RATE:
                # Message's subject to send
                message_subject = f"{stock['Stock name']}'s Stock '{stock['Stock symbol']}': 🔺 %{format(growth_rate, '.2f')} "

                # Message Body (Get Relevant News)
                articles = get_stock_news(stock)

                # Create message body
                message_body = create_message_body(articles)

                # Send Mail
                send_mail(message_subject, message_body)
            elif growth_rate < MAX_DECREASE_RATE:

                # Message's subject to send
                message_subject = f"{stock['Stock name']}'s Stock '{stock['Stock symbol']}': 🔻 %{format(growth_rate, '.2f')} "

                # Message Body (Get Relevant News)
                articles = get_stock_news(stock)

                # Create message body
                message_body = create_message_body(articles)

                # Send Mail
                send_mail(message_subject, message_body)
            else:
                print("There is no major fluctuations.")
        time.sleep(WAITING_TIME)


# ---------------------------- Run Program------------------------------- #
main()
