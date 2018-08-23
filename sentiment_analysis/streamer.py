from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json

print("Enter the Term you want to Search!")
term = raw_input()

import sentiment_mod as s

#consumer key, consumer secret, access token, access secret.
ckey = 'FQoIuXO7XqU0trJmSFQDQBZj6'
csecret = 'IfjJRtjsLBHJL7sw7Vb2OAlkJpJNPfsd9CXKpbsP1RgzRHeGyV'
atoken = '237709632-InbEzYzIk716e3UTspbdcyZ5WAalnSDIYk6647SV'
asecret = 'sFHMVORSyLa6eIRgeK2238goLwFpbxKHo8yaMKVjZ6E6v'


class listener(StreamListener):

    def on_data(self, data):

		all_data = json.loads(data)

		tweet = all_data["text"]
		sentiment_value, confidence = s.sentiment(tweet)
		print(tweet, sentiment_value) 

		if confidence*100 >= 80:
			output = open("twitter-out.txt","a")
			output.write(sentiment_value)
			output.write('\n')
			output.close()

		return True

    def on_error(self, status):
        print(status)

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=[term])