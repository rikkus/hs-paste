import cgi
import re
import datetime
import tenjin

from tenjin.helpers import *

from datetime import *

from pygments import highlight
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

shared_cache = tenjin.GaeMemcacheCacheStorage()
engine = tenjin.Engine(cache=shared_cache)

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class Paste(db.Model):

	id = db.IntegerProperty()
	author = db.UserProperty()
	code = db.TextProperty()
	html = db.TextProperty()
	preview = db.StringProperty(multiline=True)
	date = db.DateTimeProperty()

class Handler(webapp.RequestHandler):

	def render(self, template_name, context):
		self.response.out.write(
			engine.render('templates/' + template_name + '.html', context)
		)

class PasteForm(Handler):

	def get(self):
		Handler.render(self, 'form', {})

class PasteViewer(Handler):

	def get(self):
		id = re.sub(r'/', '', self.request.path)
		paste = db.GqlQuery('SELECT * FROM Paste WHERE id = ' + id)[0]
		context = {
			'date': paste.date.strftime(DATE_FORMAT),
			'html': paste.html
		}
		Handler.render(self, 'viewer', context)

class PasteRecent(Handler):

	def get(self):
		pastes = db.GqlQuery('SELECT * FROM Paste ORDER BY date DESC LIMIT 5')
		context = { 'pastes': pastes }
		Handler.render(self, 'recent', context)

class PasteSaver(Handler):

	def post(self):
		paste = self.create_paste(
			self.next_id(),
			self.request.get('code'),
			users.get_current_user()
		)
		paste.put()
		self.redirect('/' + str(paste.id))

	def next_id(self):
		result = db.GqlQuery('SELECT * FROM Paste ORDER BY id DESC LIMIT 1')
		if result.count() > 0:
			return int(result[0].id) + 1
		else:
			return 1

	def create_paste(self, id, code, user):
		paste = Paste()
		paste.id = id
		paste.user = user
		paste.code = code
		lexer = guess_lexer(code)
		formatter = HtmlFormatter()
		paste.html = highlight(code, lexer, formatter)
		preview = str.join("\n", code.splitlines()[0:5])
		paste.preview = highlight(preview, lexer, formatter)
		paste.date = datetime.utcnow()
		return paste
	
application = webapp.WSGIApplication(
	[
		('/', PasteForm),
		('/[0-9]+', PasteViewer),
		('/recent', PasteRecent),
		('/save', PasteSaver)
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

