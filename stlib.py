# Library for Stalker project

#Libraries 
import pandas as pd
import seaborn as sns
from IPython.display import Image, display
import matplotlib.pyplot as plt
# Google search
from googlesearch import search
# Tldextract to get domain of url
import tldextract as tld
# BeautifulSoup
from bs4 import BeautifulSoup as bs
from bs4.element import Comment
import urllib.request
# NLTK to analyze webs
import nltk
from nltk.corpus import stopwords
from nltk import FreqDist
from nltk.tokenize import word_tokenize
# Find close matches
from difflib import get_close_matches
# Sentiment analysis
from textblob import TextBlob
# Twitter sentiment analysis
import tweepy
# News API
from newsapi import NewsApiClient
# Credentials
import credentials as cd

# Finding info in APIs
newsapi = NewsApiClient(api_key=cd.news_credentials['api_key'])
news_sources = 'the-verge,buzzfeed,engadget,hacker-news,mashable,reddit-r-all,wired,techcrunch'

# Twitter API
consumer_key = cd.twitter_credentials['consumer_key']
consumer_key_secret = cd.twitter_credentials['consumer_key_secret']
access_token = cd.twitter_credentials['access_token']
access_token_secret = cd.twitter_credentials['access_token_secret']

auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Finding query on Google

# Finding related urls

def find_webs(query):
    urls = []
    rrss = ['facebook', 'twitter', 'linkedin', 'instagram', 'youtube','pinterest','angel']
    sites = []
    red_social = False
    for s in search(query, tld="com", num=30, stop=30, pause=3, lang='en'):

        if len(urls)<10:
            for rs in rrss:
                if rs in s or tld.extract(s).domain in sites:
                    red_social = True
            if not red_social and s not in urls:
                urls.append(s)
                sites.append(tld.extract(s).domain)  

            red_social = False
    return urls

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body):
    soup = bs(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def cleaning_urls_text(url):
    try:
        html = text_from_html(urllib.request.urlopen(url).read())
        stop_words = set(stopwords.words('english')) 
        word_tokens = word_tokenize(html)
        return [w for w in word_tokens if not w in stop_words]
    except:
        return []

def filter_warning_words(sentence):
    warning_word = ['lie', 'fraud', 'scam', 'extortion', 'deceit', 'crime','arson', 'assault', 'bigamy', 'blackmail',
                'bribery', 'burglary', 'child abuse', 'conspiracy', 'espionage', 'forgery', 'fraud', 'genocide', 
                'hijacking','homicide', 'kidnapping', 'manslaughter', 'mugging', 'murder', 'perjury', 'rape', 'riot',
                'robbery', 'shoplifting', 'slander', 'smuggling', 'treason', 'trespassing']
    return list(filter(lambda word: word in warning_word, sentence))

def warnings_count(url):
    clean_sentence = cleaning_urls_text(url)
    length = len(filter_warning_words(clean_sentence))
    return (url, length) if length != 0 else None 

def most_warnings(urls):
    list_len_tup = list(map(warnings_count, urls))
    list_len_tup_clean = list(filter(lambda item: item != None, list_len_tup))
    list_len_tup_clean.sort(key = lambda item: item[1], reverse=True)
    top_urls = [url for url, length in list_len_tup_clean[:2]]
    
    if len(top_urls) > 1:
        print(f"""
        We found something sketchy. You might want to check these links:
        
            - {top_urls[0]}
            
            - {top_urls[1]}
        """)
    elif len(top_urls) == 1:
        print(f"""
        We found something sketchy. You might want to check this link:
            {top_urls[0]}
        """)
    else:
        print(f"We couldn't find anything worrying  about X") 
        
# Input correction
def retrieve_name(my_name, companies):
    companies_list = []
    for i in companies.dropna(subset=['name']).name:
        companies_list.append(i)
    
    if my_name in companies_list:
        return my_name
    elif len(get_close_matches(my_name, companies_list)) > 0:
        action = input("Did you mean %s instead? [y or n]: " % get_close_matches(my_name, companies_list)[0])
        if (action == "y"):
            return get_close_matches(my_name, companies_list)[0]
        elif (action == "n"):
            return my_name
        else:
            return("we don't understand you. Apologies.")

def retrieve_sector(my_sector, investments):
    investments = investments.dropna(subset=['raised_amount_usd', 'company_category_list'])
    sector_list0 = []
    sector_list = []
    for item in investments['company_category_list']:
        if ',' in item:
            sector_list0.append(item.split(sep=', '))
        else:
            sector_list0.append(item)
    for i in sector_list0:
        if type(i) == list:
            for sec in i:
                sector_list.append(sec)

        else:
            sector_list.append(i)
    if my_sector in sector_list:
        return my_sector
    elif len(get_close_matches(my_sector, sector_list)) > 0:
        action = input("Did you mean %s instead? [y or n]: " % get_close_matches(my_sector, sector_list) [0])
        if (action == "y"):
            return get_close_matches(my_sector, sector_list)[0]
        else:
            return my_sector

 # Sentiment analysis tweeter
def tw_sent_sector(public_tweets, sector):    
    sentiment_list = []
    for tweet in public_tweets:
        analysis = TextBlob(tweet.text)
        sentiment_list.append(analysis.sentiment[0])
    if sum(sentiment_list)>0:
         sent = 'Positive'
    elif sum(sentiment_list)<0:
        sent = 'Negative'
    else:
        sent = 'Neutral'
    print(f"The sentiment about {sector} industry in Twitter is {sent}")
    
    
# Sentiment analysis news
def news_sentiment_sector(public_news, sector):
    news_list = []
    for piece in range(len(public_news['articles'])):
        news_list.append(TextBlob(public_news['articles'][piece]['title']).sentiment[0])
        news_list.append(TextBlob(public_news['articles'][piece]['description']).sentiment[0]) 
    if sum(news_list)>0:
        news_sent = 'Positive'
    elif sum(news_list)<0:
        news_sent = 'Negative'
    else:
        news_sent = 'Neutral'
    print(f"There have been {len(public_news)} news pieces about {sector} industry recently and are in general {news_sent}")

# Look for data about sector    
def category(sector, investments):
    # Gather tweets
    public_tweets = api.search(sector)
    
    # Gather news
    public_news = newsapi.get_everything(q=sector,sources=news_sources,language='en')
    
    # Prepare the data for the sector
    investments = investments.dropna(subset=['company_category_list'])
    sector_investments = investments[investments['company_category_list'].str.contains(sector)].drop('index',axis=1)
    sector_investments.reset_index(drop=True)
    sector_investments['funded_at'] = pd.to_datetime(sector_investments['funded_at'])
    sector_investments['Year'] = sector_investments['funded_at'].apply(lambda x: x.year )
    sector_investments['Month'] = sector_investments['funded_at'].apply(lambda x: x.month )
    sector_investments['Day'] = sector_investments['funded_at'].apply(lambda x: x.day )
    
    # Sentiment analysis Twitter
    tw_sent_sector(public_tweets, sector)
    
    # Sentiment analysis News
    news_sentiment_sector(public_news, sector)
    
    # create plot
    sector_year = sector_investments.groupby(['Year']).sum()[-10:]
    movement = ((sector_year.raised_amount_usd.iloc[len(sector_year)-1] -sector_year.raised_amount_usd.iloc[0])/sector_year.raised_amount_usd.iloc[0]*100)
    if sector_year.raised_amount_usd.iloc[0] + sector_year.raised_amount_usd.iloc[len(sector_year)-1] >= 0:
        in_dec = 'increased'
        grow = 'growing'
    else:
        in_dec = 'decreased'
        grow = 'falling'
        movement = movement[1:]
    sns.lineplot(x=sector_year.index, y=sector_year.raised_amount_usd).set_title(f'Evolution of the amount invested in {sector}')
    peak_year =  sector_year.index[sector_year['raised_amount_usd']== max(sector_year.raised_amount_usd)].to_list()
    peak_amount = max(sector_year.raised_amount_usd)
    low_amount = min(sector_year.raised_amount_usd)
    low_year = sector_year.index[sector_year['raised_amount_usd']== min(sector_year.raised_amount_usd)].to_list()
    format_doll = ',.2f'
    print(f"""The amount of money invested in {sector} companies has {in_dec} by {format(abs(movement),format_doll)}% in the last {len(sector_year)} years, 
it is expected to keep {grow} by X the next  X years. 
It peaked in year {peak_year} with ${format(peak_amount,format_doll)} invested and its lowest point was in year {low_year} with ${format(low_amount,format_doll)} invested.""")
    plt.ylabel('Raised amount in USD')
    plt.show()
    investments_per_year = sector_investments.groupby(['Year']).count()
    sns.lineplot(x=investments_per_year.index[-10:], y=investments_per_year.Day[-10:]).set_title(f'Evolution of the number of investment in {sector}')
    plt.ylabel('Number of investments')
    print("""Plot explanaition average investment
    
    """)
    plt.show()
    
 # Sentiment analysis founder
def tw_analysis_founder(public_tweets, founder):
    sentiment_list = []
    for tweet in public_tweets:
        analysis = TextBlob(tweet.text)
        sentiment_list.append(analysis.sentiment[0])
    if sum(sentiment_list)>0:
         sent = 'Positive'
    elif sum(sentiment_list)<0:
        sent = 'Negative'
    else:
        sent = 'Neutral'
    print(f"The sentiment about {founder} in Twitter is {sent}")
            

# Look for data about the founder
def founders(founder, people):
    full_name = founder.split()
    public_tweets = api.search(founder)
    for i in range(len(people)):
        if people.first_name.iloc[i] == full_name[0] and people.last_name.iloc[i]==full_name[1]:
            display(Image(url=people.profile_image_url[i]))
            print(f'We found this information about {founder}:')
            print(f"Founder's name: {people.first_name[i]} {people.last_name[i]} ")
            print(f"Title: {people.title[i]}")
            print(f"Organization: {people.organization[i]}")
            print(f"Location: {people.location_city[i]}, {people.location_region[i]}, {people.location_country_code[i]}")
            if people.twitter_url[i] != None:
                print(f"Twitter URL: {people.twitter_url[i]}")
            if people.linkedin_url[i] != None:
                print(f"Linkedin URL: {people.linkedin_url[i]}")
            if people.facebook_url[i] != None:
                print(f"Facebook URL: {people.facebook_url[i]}")
    # Twitter analysis
    tw_analysis_founder(public_tweets, founder)
    # Google search
    most_warnings(find_webs(founder))
 