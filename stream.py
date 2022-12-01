import tweepy
from kafka import KafkaProducer
import json
import pytz
import config.config as config

BEARER_TOKEN = config.BEARER_TOKEN
ALL_EXPANSIONS = ["author_id", "referenced_tweets.id", "edit_history_tweet_ids", "in_reply_to_user_id", "attachments.media_keys", "attachments.poll_ids", "geo.place_id", "entities.mentions.username", "referenced_tweets.id.author_id",]
ALL_MEDIA_FIELDS = ["media_key", "type", "url", "duration_ms", "height", "preview_image_url", "public_metrics", "width", "alt_text", "variants",]
ALL_PLACE_FIELDS = ["full_name", "id", "contained_within", "country", "country_code", "geo", "name", "place_type",]
ALL_POLL_FIELDS = ["id", "options", "duration_minutes", "end_datetime", "voting_status",]
ALL_TWEET_FIELDS = ["id", "text", "attachments", "author_id", "context_annotations", "conversation_id", "created_at", "entities", "geo", "in_reply_to_user_id", "lang", "possibly_sensitive", "public_metrics", "referenced_tweets", "reply_settings", "source", "withheld",]
ALL_USER_FIELDS = ["id", "name", "username", "created_at", "description", "entities", "location", "pinned_tweet_id", "profile_image_url", "protected", "public_metrics", "url", "verified", "withheld",]
WIB = pytz.timezone('Asia/Jakarta')

class TwitterStreamingClient(tweepy.StreamingClient):
    def __init__(self, bearer_token):
        super().__init__(bearer_token)
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda m: json.dumps(m).encode('utf-8'),
        )
      
    def on_response(self, response):
        
        data = response.data
        matching_rules = response.matching_rules
        if "users" in response.includes:
            users_dict = {user.id:user for user in response.includes["users"]}
        if "places" in response.includes:
            places_dict = {place.id:place for place in response.includes["places"]}
        if "tweets" in response.includes:
            tweets_dict = {tweet.id:tweet for tweet in response.includes["tweets"]}

        if data is not None:
            tags = [matching_rule.tag.split(';') for matching_rule in matching_rules]
            
            lat, long = 0.0, 0.0
            if data.geo:
                lat1, long1, lat2, long2 = places_dict[data.geo["place_id"]].geo["bbox"]
                lat, long = (lat1+lat2)/2, (long1+long2)/2
            
            message = {
                "id" : data.id,
                "author_username" : users_dict[data.author_id].username,
                "created_at" : data.created_at.astimezone(WIB).isoformat(),
                "text" : data.text,
                "lat" : lat, "long" : long,
                "source" : data.source,
                "retweet_count" : data.public_metrics["retweet_count"],
                "reply_count" : data.public_metrics["reply_count"],
                "like_count" : data.public_metrics["like_count"],
                "quote_count" : data.public_metrics["quote_count"],
                "possibly_sensitive" : data.possibly_sensitive,
                "tags" : [tag[0] for tag in tags],
            }
            
            if data.geo:
                print(message)

            self.producer.send(tags[0][1], message)

            # print(message)
            

streaming_client = TwitterStreamingClient(BEARER_TOKEN)
print(f"Rule used: {streaming_client.get_rules()}")


streaming_client.filter(
    expansions=ALL_EXPANSIONS,
    media_fields=ALL_MEDIA_FIELDS,
    place_fields=ALL_PLACE_FIELDS,
    poll_fields=ALL_POLL_FIELDS,
    tweet_fields=ALL_TWEET_FIELDS,
    user_fields=ALL_USER_FIELDS
)