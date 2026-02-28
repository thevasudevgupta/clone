import os

import tweepy


def get_tweepy():
    # $1 for client.get_users_following(user_id, user_auth=True)
    # $0.5 for client.get_home_timeline()
    # $0.01 for client.create_tweet(text=...)
    # $0.05 for get_users_tweets(user_id)
    return tweepy.Client(
        consumer_key=os.getenv("X_CONSUMER_KEY"),
        consumer_secret=os.getenv("X_CONSUMER_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
    )


class TwitterClient:
    # TODO: add support of quote tweet, reply tweet?
    def __init__(self):
        self.client = get_tweepy()

    def _get_text(self, tweet):
        return tweet.note_tweet["text"] if hasattr(tweet, "note_tweet") else tweet.text

    def get_tweet(self, tweet_id: str):
        kwargs = {
            "user_auth": True,
            "tweet_fields": ["conversation_id", "author_id", "note_tweet"],
        }
        tweet = self.client.get_tweet(tweet_id, **kwargs).data
        # TODO: why do we need to handle 1st tweet separately?
        res = [self._get_text(tweet)]
        query = f"conversation_id:{tweet.conversation_id} from:{tweet.author_id}"
        thread = self.client.search_recent_tweets(query=query, **kwargs)
        if thread.data is not None:
            for tweet in sorted(thread.data, key=lambda x: x.id):
                res += [self._get_text(tweet)]
        return "\n".join(res)

    def create_tweet(self, tweet):
        self.client.create_tweet(text=tweet)
