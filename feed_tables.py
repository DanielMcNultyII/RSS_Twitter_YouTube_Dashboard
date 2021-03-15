# Daniel McNulty II
# Functions needed to make the dashboard to show user's RSS feed, Twitter feed, and YouTube subscription videos in one
# place possible.


# Import necessary libraries/functions
import dash_bootstrap_components as dbc
import dash_html_components as html
import datetime
import dateutil.parser
import feedparser
import itertools
from html2text import html2text
import pandas as pd
import pytz
from twitter import Api as TwitterDataApi
from youtube_api import YoutubeDataApi


# Set the UTC timezone implementation to variable utc. This will be used to standardize the times for each RSS feed
# article in order to properly sort them by recency.
utc = pytz.UTC


# int_check() function to handle RSS feed summaries that are not clean strings, but rather a smorgasbord of text that
# could include HTML formatting and the full article. It looks for a brk_char, which in this case is set to <p> or </p>.
# If the brk_char is in the input string, the function returns where the brk_char was found. If it isn't, then the
# function returns 0 if the input brk_char is <p> or the length of the input string if the brk_char is anything else.
# Future updates could look to take a more refined approach to cleaning the summaries of articles.
def int_check(strng, brk_char):
    val = strng.find(brk_char)
    if val != -1 and isinstance(val, int):
        return val
    else:
        if brk_char == '<p>':
            return 0
        else:
            return len(strng)


# This function takes the list of RSS feeds (url_list) and generates a dash bootstrap components table of the most
# recent articles from that list of RSS feeds. The number of articles is capped at the number stored in max_listings.
def news_feed(url_list, max_listings):
    # Parse through all RSS feeds in the url_list to extract all their articles.
    feeds = [feedparser.parse(url)['entries'] for url in url_list]
    # Combine all feeds articles into 1 combined list, then sort the articles by date/time published.
    combined_feed = [item for feed in feeds for item in feed]
    combined_feed.sort(key=lambda x: dateutil.parser.parse(x['published']).replace(tzinfo=utc), reverse=True)
    # Set up a dictionary where the key is the time the dictionary was created and the value is a list of the most
    # recent articles, capped at the number stored in max_listings.
    news_dict = {"Last update : " + datetime.datetime.now().strftime("%H:%M:%S"):
                 [[html.A([html.H5(entry.title),
                           html.H6(entry.author + ' | ' + entry.title_detail.base),
                           html.P(html2text(
                               entry.summary[int_check(entry.summary, '<p>'):int_check(entry.summary, '</p>')])
                                   .replace('\n', ' '))],
                          href=entry.link, target='_blank')]
                  for entry in combined_feed[:max_listings]]}
    # Create a dataframe from the dictionary created above.
    news_df = pd.DataFrame(news_dict)
    # Return a dash bootstrap components table created from the dataframe created above.
    return dbc.Table.from_dataframe(news_df)


# This function returns the Twitter lists of the Twitter user whose Twitter API credentials are input in the function.
# It returns the lists in a dictionary with inputs of the lists names and values in a format to be used in a dash
# dropdown. Future updates can make the Twitter API credentials function inputs rather than have them be hardcoded.
def twitter_lists():
    twitter_api = TwitterDataApi(consumer_key='INSERT YOURS HERE',
                                 consumer_secret='INSERT YOURS HERE',
                                 access_token_key='INSERT YOURS HERE',
                                 access_token_secret='INSERT YOURS HERE')

    uls = twitter_api.GetLists()
    return [{'label': l_d['name'], 'value': str(l_d['id'])} for l_d in [l.AsDict() for l in uls]]


# This function takes the input Twitter list (l_id) and generates a dash bootstrap components table of the most recent
# tweets from the members of that list. The number of tweets is capped at the number stored in max_tweets. Future
# updates can make the Twitter API credentials function inputs rather than have them be hardcoded.
def twitter_feed(l_id, max_tweets):
    # Set Twitter API
    twitter_api = TwitterDataApi(consumer_key='INSERT YOURS HERE',
                                 consumer_secret='INSERT YOURS HERE',
                                 access_token_key='INSERT YOURS HERE',
                                 access_token_secret='INSERT YOURS HERE')
    # Get the most recent tweets from the Twitter list specified by l_id. The number of tweets is capped at the number
    # stored in max_tweets.
    list_tl = twitter_api.GetListTimeline(list_id=int(l_id), count=max_tweets, return_json=True)
    # Set up a dictionary where the first key is blank and the values are the Twitter avatars of the members of the list
    # whom the tweets belong to. Then the second key is the time the dictionary was created and the second value is a
    # list of the most recent tweets, capped at the number stored in max_tweets from before.
    tweet_dict = {'': [html.A(html.Img(src=list_tl[i]['user']['profile_image_url_https']),
                              href='https://www.twitter.com/' + list_tl[i]['user']['screen_name'],
                              target='_blank')
                       for i in range(0, len(list_tl))],
                  "Last update : " + datetime.datetime.now().strftime("%H:%M:%S"):
                      [html.A([html.H5(list_tl[i]['user']['name']), html.P(html2text(list_tl[i]['text']))],
                              href='https://www.twitter.com/' + list_tl[i]['user']['screen_name'] + '/status/'
                              + list_tl[i]['id_str'],
                              target='_blank')
                       for i in range(0, len(list_tl))]}
    # Create a dataframe from the dictionary created above.
    tweet_df = pd.DataFrame(tweet_dict)
    # Return a dash bootstrap components table created from the dataframe created above.
    return dbc.Table.from_dataframe(tweet_df)


# This function takes the input YouTube ID (yt_id_ and generates a dash bootstrap components table of the most recent
# uploads or livestreams (Determined by e_type) from the user's subscriptions. The number of videos taken from each
# subscribed channel is capped at the number stored in max_vids. The maximum number of videos to be held in the returned
# table is capped at 10. Future updates can make the YouTube API credential and the maximum number of videos to have in
# the returned table function inputs rather than have them be hardcoded.
def youtube_feed(yt_id, e_type=None, max_vids=1):
    # Set YouTube API
    yt_api = YoutubeDataApi('INSERT YOURS HERE')
    # Get the user's subscriptions
    sub_list = yt_api.get_subscriptions(yt_id)
    # Search for each subscribed channel and return the most recent videos from said channel. Videos returned per
    # channel is capped by the number stored in max_vids
    recent_vids = [yt_api.search(sub_list[i]['subscription_title'], channel_id=sub_list[i]['subscription_channel_id'],
                                 event_type=e_type, max_results=max_vids, order_by='date')
                   for i in range(0, len(sub_list))]
    # Remove the YouTube API since it is no longer needed and Google hard-caps the quota you can use on it.
    del yt_api
    # Iterate through the videos in recent_vids and sort them by upload date/time
    vid_list = list(itertools.chain(*recent_vids))
    vid_list.sort(key=lambda x: x['video_publish_date'], reverse=True)
    # Set up a dictionary where the first key is blank and the values are the video thumbnails of the videos in the
    # recent_vids list. Then the second key is the time the dictionary was created and the second value is a
    # list of the most recent videos, capped at either the minimum of the length of recent_vids and 10.
    yt_dict = {'': [html.A(html.Img(src=vid_list[i]['video_thumbnail']),
                    href='https://www.youtube.com/watch?v=' + vid_list[i]['video_id'],
                    target='_blank')
                    for i in range(0, min(len(vid_list), 10))],
               "Last update : " + datetime.datetime.now().strftime("%H:%M:%S"):
                   [[html.A(html.H6(html2text(vid_list[i]['video_title'])),
                     href='https://www.youtube.com/watch?v=' + vid_list[i]['video_id'],
                     target='_blank'),
                     html.A(html.P(vid_list[i]['channel_title']),
                     href='https://www.youtube.com/channel/' + vid_list[i]['channel_id'],
                     target='_blank')
                     ] for i in range(0, min(len(vid_list), 10))]}
    # Create a dataframe from the dictionary created above.
    yt_df = pd.DataFrame(yt_dict)
    # Return a dash bootstrap components table created from the dataframe created above.
    return dbc.Table.from_dataframe(yt_df)
