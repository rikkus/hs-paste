import datetime
import re
import hspaste

from datetime import *

from pygments import highlight
from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import webapp

class Save(hspaste.Handler):

	def post(self):
		language = self.request.get('language')
		other_language = self.request.get('other')
		code = self.request.get('code')

		if language == 'other':
			language = other_language

		paste = self.create_paste(code, language)
		key = paste.put()
		self.send_mail(paste, key.id())
		self.redirect('/' + str(key.id()))

	def create_paste(self, code, language):
		paste = hspaste.Paste()
		paste.code = code
		lexer = get_lexer_by_name(language)
		paste.language = lexer.name
		formatter = HtmlFormatter()
		paste.html = highlight(code, lexer, formatter)
		preview = str.join("\n", code.splitlines()[0:5])
		paste.preview = highlight(preview, lexer, formatter)
		paste.date = datetime.utcnow()
		return paste

	def send_mail(self, paste, id):
		message = mail.EmailMessage()
		message.sender = 'rikkus@gmail.com'
		message.reply_to = paste.author.email()
		message.to = 'rikkus@gmail.com'
		message.subject = 'paste ' + str(id) + ' (' + paste.language + ')'
		message.body = paste.code
		message.html = paste.html
		message.send()

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
				{'id':'css', 'name':'CSS'},
				{'id':'ruby', 'name':'Ruby'},
				{'id':'python', 'name':'Python'}
			],
			'all_languages': all_languages
		}
		self.render('form', context)


class Recent(hspaste.Handler):

	def get(self):
		pastes = hspaste.Paste.gql('ORDER BY date DESC LIMIT 5')
		context = { 'pastes': pastes }
		self.render('recent', context)

class Show(hspaste.Handler):

	def get(self):
		id = re.sub(r'/', '', self.request.path)
		paste = hspaste.Paste.get_by_id(int(id))
		author = paste.author if paste.author else ''
		context = {
			'date': paste.date.strftime(hspaste.Handler.DATE_FORMAT),
			'language': paste.language,
			'html': paste.html,
			'author': paste.author
		}
		self.render('viewer', context)

