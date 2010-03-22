import datetime
import re
import hspaste

from datetime import *

from pygments import highlight
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter

from google.appengine.ext import db
from google.appengine.api import users

class Save(hspaste.Handler):

	def post(self):

		language = self.request.get('language')

		if language == 'other':
			language = self.request.get('other')

		paste = self.create_paste(
			self.next_id(),
			self.request.get('code'),
			language,
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

	def create_paste(self, id, code, language, user):
		paste = hspaste.Paste()
		paste.id = id
		paste.user = user
		paste.code = code

		if language and language != 'auto':
			lexer = get_lexer_by_name(language)
		else:
			lexer = guess_lexer(code)

		paste.language = lexer.name

		formatter = HtmlFormatter()
		paste.html = highlight(code, lexer, formatter)
		preview = str.join("\n", code.splitlines()[0:5])
		paste.preview = highlight(preview, lexer, formatter)
		paste.date = datetime.utcnow()
		return paste

class Form(hspaste.Handler):

	def get(self):

		all_languages = []

		for l in self.lexers():
			all_languages.append({'id':l[1][0], 'name':l[0]})
			
		context = {
			'base_languages': [
				{'id':'csharp', 'name':'C#'},
				{'id':'sql', 'name':'SQL'},
				{'id':'xml', 'name':'XML'},
				{'id':'css', 'name':'CSS'}
			],
			'all_languages': all_languages
		}
		self.render('form', context)


class Recent(hspaste.Handler):

	def get(self):
		pastes = db.GqlQuery('SELECT * FROM Paste ORDER BY date DESC LIMIT 5')
		context = { 'pastes': pastes }
		self.render('recent', context)

class Show(hspaste.Handler):

	def get(self):
		id = re.sub(r'/', '', self.request.path)
		paste = db.GqlQuery('SELECT * FROM Paste WHERE id = ' + id)[0]
		context = {
			'date': paste.date.strftime(hspaste.Handler.DATE_FORMAT),
			'language': paste.language,
			'html': paste.html,
			'author': paste.author
		}
		self.render('viewer', context)

