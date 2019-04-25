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

def most_warnings(urls, look_for):
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
        print(f"We couldn't find anything worrying about {look_for} on Google. Nice!")
   
        
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
    investments_per_year = sector_investments.groupby(['Year']).count()
    peak_year =  sector_year.index[sector_year['raised_amount_usd']== max(sector_year.raised_amount_usd)].to_list()
    peak_amount = max(sector_year.raised_amount_usd)
    #peak_year_invest =  investments_per_year.index[investments_per_year['raised_amount_usd']== max(investments_per_year.raised_amount_usd)].to_list()
    low_amount = min(sector_year.raised_amount_usd)
    most_invested_companies = sector_investments.groupby(by='company_name').sum().sort_values(by='raised_amount_usd', ascending=False)
    low_year = sector_year.index[sector_year['raised_amount_usd']== min(sector_year.raised_amount_usd)].to_list()
    format_doll = ',.2f'
    print(f"""The amount of money invested in {sector} companies has {in_dec} by {format(abs(movement),format_doll)}% in the last {len(sector_year)} years. 
It peaked in year {peak_year[0]} with ${format(peak_amount,format_doll)} invested and its lowest point was in year {low_year[0]} with ${format(low_amount,format_doll)} invested.
""")
    
    plt.ylabel('Raised amount in USD')
    plt.show()
    
    sns.lineplot(x=investments_per_year.index[-10:], y=investments_per_year.Day[-10:]).set_title(f'Evolution of the number of investment in {sector}')
    plt.ylabel('Number of investments')
 
    #print("""Plot explanaition average investment
    
    """)
    plt.show()
    #print(f"""
    
   # The Top 3 companies with biggest investments are:
    #- {most_invested_companies.index[0]} with ${most_invested_companies.raised_amount_usd[0]} raised,
    #- {most_invested_companies.index[1]} with ${most_invested_companies.raised_amount_usd[1]} raised and
    #- {most_invested_companies.index[2]} with ${most_invested_companies.raised_amount_usd[2]} raised
   
    #""")
    
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
    # What to search on Google
    look_for = founder
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
      
    most_warnings(find_webs(founder), look_for)
    
    

# Look for data about company
def find_companies_by_size(size, companies, name, sector, company):
    company_nan = companies.dropna()
    company_sector = company_nan[company_nan['category_list'].str.contains(sector)].drop('index',axis=1).dropna()
    company_sector['total_funding_size']=pd.qcut(company_sector.funding_total_usd, q=[0, .25, .75, 1], labels=['small', 'medium', 'big'])
    if name in company_nan['name']:
        return company_sector[(company_sector['total_funding_size']==size)& (company_sector['funding_total_usd'] > 100000) & (company_sector['status'] != 'closed')& (company_sector['country_code']==company.country_code)].sample()
    else:     
        return company_sector[(company_sector['total_funding_size']==size)& (company_sector['funding_total_usd'] > 100000) & (company_sector['status'] != 'closed')].sample()
 


def competitor_info(company):
    print(f"Company name: {company.name.item()}")
    print(f"Total money raised: ${format(company.funding_total_usd.item(),',.2f')}")
    print(f"Total rounds: {company.funding_rounds.item()}")
    print(f"Webpage: {company.homepage_url.item()}")
    print(f"Country: {company.country_code.item()}")
    print(f"Status: {company.status.item()}")
    print(f"Founded in: {company.founded_at.item()}")

# Sentiment analysis company
def tw_analysis_company(public_tweets, company):
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
    print(f"The sentiment about {company} in Twitter is {sent}")
        

def startup(name, companies, sector):
    company = companies[companies['name'] == name]
    # What to search on Google
    look_for = name
     # Gather tweets
    public_tweets = api.search(name)
    try:
        print(f"Company name: {company.name.item()}")
        print(f"Total money raised: ${format(company.funding_total_usd.item(),',.2f')}")
        print(f"Total rounds: {company.funding_rounds.item()}")
        print(f"Webpage: {company.homepage_url.item()}")
        print(f"Country: {company.country_code.item()}")
        print(f"Status: {company.status.item()}")
   
    # Find competitors
        print('\n')
        print(f"Competitors similar to {company.name.item()}:")
        print('\n')
        competitor_info(find_companies_by_size('small', companies, name, sector, company))
        print('\n')      
        competitor_info(find_companies_by_size('medium', companies, name, sector, company))
        print('\n')     
        competitor_info(find_companies_by_size('big', companies, name, sector, company))
    except: 
        print(f"We couldn't find information about {name} in Crunchbase")
    
    #Twitter sentiment analysis for company
    tw_analysis_company(public_tweets, name)
    # Google search
    most_warnings(find_webs(name), look_for)
              