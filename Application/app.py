#!/usr/bin/env python3
import tornado.httpserver
from tornado.ioloop import IOLoop
import signal
import tornado.options
import tornado.web
import tornado.httpclient

import urllib
import json
import datetime
import time
import uvloop
#from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio

from tornaduv import UVLoop
#IOLoop.configure(UVLoop)


from custom_logging import logger
from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

#http://steelkiwi.com/blog/jwt-authorization-python-part-1-practise/

class IndexHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		query = self.get_argument('q')
		client = tornado.httpclient.AsyncHTTPClient()
		client.fetch("http://search.twitter.com/search.json?" + \
				urllib.urlencode({"q": query.encode('utf8'), "result_type": "recent", "rpp": 100}),
				callback=self.on_response)

	def on_response(self, response):
		body = json.loads(response.body)
		result_count = len(body['results'])
		now = datetime.datetime.utcnow()
		raw_oldest_tweet_at = body['results'][-1]['created_at']
		oldest_tweet_at = datetime.datetime.strptime(raw_oldest_tweet_at,
				"%a, %d %b %Y %H:%M:%S +0000")
		seconds_diff = time.mktime(now.timetuple()) - \
				time.mktime(oldest_tweet_at.timetuple())
		tweets_per_second = float(result_count) / seconds_diff
		self.write("""
<div style="text-align: center">
	<div style="font-size: 72px">%s</div>
	<div style="font-size: 144px">%.02f</div>
	<div style="font-size: 24px">tweets per second</div>
</div>""" % (self.get_argument('q'), tweets_per_second))
		self.finish()


from LoginModule.login import Login
from SignupModule.signup import Signup
from settings import mongo_db
app_urls = [(r"/", IndexHandler), 
			(r"/login", Login),
			(r"/signup$", Signup),
			(r"/signup/(\d+$)", Signup),
			(r"/signup/([a-zA-Z0-9_.-]*$)", Signup),
			
			]



def handle_signal(sig, frame):
    loop = IOLoop.instance()
    logger.info("stopping server dude")
    loop.add_callback(loop.stop)


if __name__ == "__main__":

        tornado.options.parse_command_line()
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        app = tornado.web.Application(handlers=app_urls, db=mongo_db)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        #asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        #AsyncIOMainLoop().install()
        #asyncio.get_event_loop().run_forever()
        logger.info("Application server started on %s"%options.port)

        IOLoop.instance().start()
