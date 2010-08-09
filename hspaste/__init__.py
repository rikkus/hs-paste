import operator

import tenjin

from tenjin.helpers import *

from pygments.lexers import get_all_lexers

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp

shared_cache = tenjin.GaeMemcacheCacheStorage()
engine = tenjin.Engine(cache=shared_cache)

class Paste(db.Model):

	author = db.UserProperty(auto_current_user_add=True)
	code = db.TextProperty()
	html = db.TextProperty()
	preview = db.TextProperty()
	language = db.StringProperty()
	date = db.DateTimeProperty()

class Handler(webapp.RequestHandler):

	DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

	def render(self, template_name, context):
		self.response.out.write(
			engine.render('templates/' + template_name + '.html', context)
		)

	def lexers(self):
		return sorted(list(get_all_lexers()), key=operator.itemgetter(0))

