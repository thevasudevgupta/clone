# we need basic tools which can access activity of people I follow ("following" section)
# based on that, it needs to decide what to do?
# lets start with paper posting section - it should look at what papers are trending
# and then based on that, read the paper and try to summarise the paper?
# agent should make suggestions only for now; and requires approval before posting
# agent should get triggered only once every 10 seconds?

from dotenv import load_dotenv
assert load_dotenv()
import tweepy

import os
client = tweepy.Client(
    consumer_key=os.getenv("X_CONSUMER_KEY"),
    consumer_secret=os.getenv("X_CONSUMER_SECRET"),
    access_token=os.getenv("X_ACCESS_TOKEN"),
    access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
)

user_id = client.get_me().data.id
print(user_id)
# print(client.create_tweet(text="tweet from bot"))
# users_following = client.get_users_following(user_id, user_auth=True)
# print(users_following)

# $1 for client.get_users_following(user_id, user_auth=True)
# $0.5 for client.get_home_timeline()

# $0.01 for creating tweet

# $0.05 for getting user tweet

# I will save tweet links somewhere
# agent will go through them and use get_tweet as tool
# after getting content of tweet, it can decide to fetch papers based on system prompt
# and then create a tweet about paper upon approval of user
# NOTE: we want to control WRITE action programmatically;

def get_tweet(tweet_id):
    tweet_fields = ["conversation_id", "author_id", "note_tweet"]
    tweet = client.get_tweet(tweet_id, user_auth=True, tweet_fields=tweet_fields).data
    query = f"conversation_id:{tweet.conversation_id} from:{tweet.author_id}"
    res = []
    # TODO: why do we need to handle 1st tweet separately?
    res += [tweet.note_tweet["text"] if hasattr(tweet, "note_tweet") else tweet.text]
    thread = client.search_recent_tweets(query=query, user_auth=True, tweet_fields=tweet_fields)
    for tweet in sorted(thread.data, key=lambda x: x.id):
        res += [tweet.note_tweet["text"] if hasattr(tweet, "note_tweet") else tweet.text]
    return "\n".join(res)

print(get_tweet("2026765820098130111"))
