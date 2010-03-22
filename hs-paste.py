import cgi

from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import webapp

import hspaste

from hspaste import handlers

application = webapp.WSGIApplication(
	[
		('/', hspaste.handlers.Form),
		('/[0-9]+', hspaste.handlers.Show),
		('/recent', hspaste.handlers.Recent),
		('/save', hspaste.handlers.Save)
	],
	debug=True
)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()

