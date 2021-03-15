# Daniel McNulty II
# Dashboard to show user's RSS feed, Twitter feed, and YouTube subscription videos in one place.

# Import necessary libraries/functions
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_player
import pandas as pd
from feed_tables import news_feed, twitter_lists, twitter_feed, youtube_feed


# Set the maximum entries in the RSS, Twitter, and YouTube feeds to show onscreen at any given time
max_news = 40
max_tweets = 50
max_vids = 1
# Set the number of minutes between refreshes of the RSS and Twitter feeds
min_btwn_rss_update = 10
min_btwn_tweet_update = 1


# Take the list of RSS feeds to use from the Excel file Feeds.xlsx
feeds_df = pd.read_excel('Feeds.xlsx')
rss_urls = feeds_df['RSS Feeds'].tolist()


# Get the Twitter lists of the user. Twitter API credentials are needed for this. Input them in the twitter_lists()
# function in feed_tables.py. Future updates should look to put Twitter API credentials in this file as input into the
# twitter_lists() function.
t_lists = twitter_lists()
initial_list = t_lists[0]['value']

# Set the user's YouTube API ID here.
yt_id = 'INSERT YOURS HERE'


# Initialize the Dash app
app = dash.Dash(__name__, prevent_initial_callbacks=True)


# Set the app layout
app.layout = html.Div(children=[
    # Set the header of the app. This will hold the column headings and the Twitter list dropdown
    html.Div(className='wrapper', children=[
        # RSS Feed heading
        html.Div(className='left', children=html.H1('RSS Feed')),
        # Twitter Feed heading and dropdown. Dropdown consists of all the user's lists and determines which list the
        # dashboard takes tweets from.
        html.Div(className='central', children=[
            html.H1('Twitter Feed', style={'padding': 0, 'margin': 0}),
            dcc.Dropdown(
                         id='t_lists',
                         clearable=False,
                         options=t_lists,
                         value=initial_list,
                         style={'background': '#888', 'border-style': 'none', 'color': 000000,
                                'display': 'inline-block', 'height': 30, 'width': '100%', 'padding': 0, 'margin': 0},
            ),
        ]),
        # Video Feed heading. This is where YouTube streaming occurs.
        html.Div(className='right', children=html.H1('Video Feed'))
    ]),
    # Set up the RSS Feed content column. The work is primarily done by the function news_feed(), which returns a dash
    # bootstrap components table with the most recent articles from the user's RSS feeds. Refreshes based on the number
    # of minutes set at the beginning of this file in variable min_btwn_rss_update. Refresh is handled by callback
    # update_rss_feed.
    html.Div(className='column1', children=[
        html.Div(
            className='RSS_News',
            children=[html.Div(id="RSS Entries", children=news_feed(rss_urls, max_news))],
            style={'width': '100%', 'height': '87vh', 'overflowY': 'scroll'}
        ),
        dcc.Interval(
            id='rss-interval-component',
            interval=min_btwn_rss_update * 60000,  # in milliseconds
            n_intervals=0
        )
    ]),
    # Set up the Twitter Feed content column. The work is primarily done by the function twitter_feed(), which returns a
    # dash bootstrap components table with the most recent tweets from the user's selected Twitter list. Refreshes based
    # on the number of minutes set at the beginning of this file in variable min_btwn_tweet_update. Refresh is handled
    # by callback update_twitter_feed.
    html.Div(className='column2', children=[
        html.Div(
            className='Twitter_News',
            children=[html.Div(id="Twitter Entries", children=twitter_feed(initial_list, max_tweets))],
            style={'width': '100%', 'height': '87vh', 'overflowY': 'scroll'}
        ),
        dcc.Interval(
            id='tweet-interval-component',
            interval=min_btwn_tweet_update * 60000,  # in milliseconds
            n_intervals=0
        )
    ]),
    # Set up the video streaming player and content column. The streaming player uses the dash_player library's
    # DashPlayer function and a stream link input box is included to allow users to input the link they wish to stream.
    # The YouTube search is done by the callback update_yt_feed(), which is called whenever the user changes the
    # subscription search dropdown between "Uploads" and "Livestreams" or when he/she clicks the "Refresh" button. The
    # search only looks through users' subscriptions for the most recent upload by each channel he/she is subscribed to.
    html.Div(className='column3', children=[
        dash_player.DashPlayer(
            id='video-player',
            url='https://www.youtube.com/watch?v=5qap5aO4i9A',
            controls=True,
            height='34vh',
            width='100%',
        ),
        html.H4('Stream Link'),
        dcc.Input(id="video_url", type="text", placeholder="Video Link Here"),
        html.H4('Recent Videos'),
        html.Div(
            className='Youtube Vids',
            children=[html.Div(id="Youtube Entries", children='',
                               style={'height': '31vh', 'overflowY': 'scroll'})]
        ),
        html.H4('YouTube Subscription Search'),
        dcc.Dropdown(
            id='e_type',
            clearable=False,
            options=[{'label': 'Livestreams', 'value': 'live'},
                     {'label': 'Uploads', 'value': 'upload'}],
            value='upload',
            style={'background': '#888', 'border-style': 'none', 'color': 000000, 'height': 30, 'width': '100%'},
        ),
        html.Button('Refresh', id='yt_refresh', n_clicks=0, style={'margin-top': 15}),
    ]),
])


# Callback to refresh the RSS column.
@app.callback(Output('RSS Entries', 'children'),
              Input('rss-interval-component', 'n_intervals'))
def update_rss_feed(n):
    return news_feed(rss_urls, max_news)


# Callback to refresh the Twitter column.
@app.callback(Output('Twitter Entries', 'children'),
              Input('t_lists', 'value'),
              Input('tweet-interval-component', 'n_intervals'))
def update_twitter_feed(t_list, n):
    return twitter_feed(t_list, max_tweets)


# Callback to search YouTube.
@app.callback(Output('Youtube Entries', 'children'),
              Input('e_type', 'value'),
              Input('yt_refresh', 'n_clicks'))
def update_yt_feed(e_type, click):
    if e_type == 'live':
        return youtube_feed(yt_id, 'live', max_vids)
    else:
        return youtube_feed(yt_id, None, max_vids)


# Callback to set the video stream to the link input in the video_url input box.
@app.callback(
    Output("video-player", "url"),
    Input("video_url", "value"),
)
def update_output(vid_url):
    return vid_url


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(debug=False)
