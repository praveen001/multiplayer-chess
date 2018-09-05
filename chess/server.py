# Python Imports
import sys, os
import motor

# Tornado Imports
import tornado.ioloop, tornado.web, tornado.wsgi, tornado.httpserver
from tornado.options import define, parse_command_line, options

# Django Imports
import django.core.handlers.wsgi

# Configuring Django Settings Module
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..' )
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../chess')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chess.settings")

# Import Socket Handler #
from socketServer import Socket

define('port', type=int, default=8080) 

# Create A Motor Client
#client = motor.MotorClient()
#client = motor.MotorClient('mongodb://192.168.1.5:27017/chess')

# Get The Database Object
#db = motor.MotorClient('mongodb://192.168.1.5:27017/chess').chess


def main():
	wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
	tornado_app = tornado.web.Application(
	[
		(r"/static/(.*)", tornado.web.StaticFileHandler, {"path":  os.path.dirname(__file__) + 'static/'}),
		('/socket', Socket),
		('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
	])
	server = tornado.httpserver.HTTPServer(tornado_app)
	server.listen(options.port)
	#server.bind(options.port)
	#server.start(4)
	tornado_app.settings['db'] = motor.MotorClient('mongodb://127.0.0.1:27017/').chess
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
