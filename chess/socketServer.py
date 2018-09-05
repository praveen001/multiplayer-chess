import os
import sys
import json
import motor
import re
from bson import ObjectId
from tornado import websocket, gen
import tornado.wsgi
import datetime
import django.core.handlers.wsgi
from django.utils.timezone import utc
import pymongo

# List To Hold The Connected Sockets
sockets = []
admin = []
# Dict To Hold Route Functions
functions = {}

# Dict To Map Route Function
route = {
		'startGame' : 'startGame',
		'syncMove' : 'syncMove',
		'result' : 'gameResult',
		'clockSync' : 'clockSync',
		'illegal' : 'illegal',
		'adminPause' : 'adminPause',
		'adminResume' : 'adminResume',
		'adminWait' : 'adminWait',
		'adminRefresh' : 'adminRefresh',
		'gameReport' : 'gameReport',
		'isOnline' : 'isOnline',
		'redirect' : 'redirect',
		'deleteGame' : 'deleteGame',
	}

class Socket(websocket.WebSocketHandler):
	@gen.coroutine
	def open(self):
		# Convert Tornado Request To Django WSGI Request
		request = django.core.handlers.wsgi.WSGIRequest(tornado.wsgi.WSGIContainer.environ(self.request))

		Participants = self.settings['db'].participants
		Games = self.settings['db'].game
		
		exist = False
		for s in sockets:
			if s.id == request.COOKIES.get('userCookie'):
				t = yield Participants.find_one({"key" : request.COOKIES.get('userCookie') })
				print 'Duplicate Socket ' + t['username']
				exist = True
		
		if exist == False:
			
			# Get Cookie 
			if request.GET.get('id') != "admin": 
				self.id = request.COOKIES.get('userCookie')
				t = yield Participants.find_one({"key" : self.id })
			
				if t is not None:
					self.oid = str(t['_id'])
					self.username = t['username']
					self.name = t['name']
			
					# Add Socket to Socket List
					sockets.append(self)
			
					p = yield Participants.find_one({"_id" : ObjectId(self.oid) })
					games = p['games']
					games.reverse()
					gameid = None
				
					for g in games:
						if g['status'] == "pending" :
							gameid = g['gameid']
							break

					if gameid is not None:
						gs = yield Games.find_one({"_id" : ObjectId(gameid), "status" : "paused" })			
					else:		
						gs = None

					if gs is not None:
						
						# Finding other player
						user1 = yield Participants.find_one({"_id":ObjectId(gs['user1'])})
						user2 = yield Participants.find_one({"_id":ObjectId(gs['user2'])})

						print 'Found Paused Game - ' + user1['name'] + ' - ' + user2['name']
				
						if gs['user1'] == self.oid :
							k = self.id
						else:
							k = 0

						t = "restore"

						response = {
							"type" : t,
							"gameid" : gameid,
							"fen" : gs['fen'],
							"willegal" : gs['willegal'],
							"billegal" : gs['billegal'],
							"wtime" : gs['user1time'],
							"btime" : gs['user2time'],
							"turn" : gs['turn'], 
							"user1" : gs['user1'],
							"user2" : gs['user2'],
							"key" : k,
							"game" : {
								"white" : {
									"id" : str(gs['user1']),
									"key" : str(user1['key']),
									"name" : user1['name']
								},
								"black" : {
									"id" : str(gs['user2']),
									"key" : str(user2['key']),
									"name" : user2['name']
								},
								"fen" : gs['fen']
							}
						}
		
						for s in sockets:
							if s != self and (str(s.oid) == str(gs['user2']) or str(s.oid) == str(gs['user1'])):
								s.write_message(response)
								self.write_message(response)
								Games.update({ "_id" : ObjectId(gameid) },
								{
									"$set" : {
										"status" : "pending"
									}
								})

					# Console Log
					print "Socket Opened - Found Socket " + t['username']
				else:
					print "Bad Socket"
			else:
				self.oid = "admin"
				admin.append(self)
				print "Admin Socket"

	@gen.coroutine
	def on_close(self):
		Participants = self.settings['db'].participants
		Games = self.settings['db'].game
		# Convert Tornado Request To Django WSGI Request
		request = django.core.handlers.wsgi.WSGIRequest(tornado.wsgi.WSGIContainer.environ(self.request))

		if self.oid == "admin":
			# Remove Socket
			admin.remove(self)
		else:
			p = yield Participants.find_one({"_id" : ObjectId(self.oid) })
			games = p['games']
			games.reverse()
			gameid = None
			for g in games:
				if g['status'] == "pending" :
					gameid = g['gameid']
					break

			if gameid is not None:
				response = {
					"type" : "pause"
				}	
			
				gs = yield Games.find_one({"_id" : ObjectId(gameid), "status" : "pending" })
			
				if gs is not None:
					Games.update( {"_id":ObjectId(gameid)}, { "$set" : { "status" : "paused" } } )
					try:
						for s in sockets:
							if s != self and str(s.oid) == str(gs['user1']) :
								s.write_message(response)
							if s != self and str(s.oid) == str(gs['user2']) :	
								s.write_message(response)
					except:
						print sys.exc_info()[0]
			sockets.remove(self)

			# Just Console Logging
		print "Socket Closed"

	def on_message(self, message):
		# Convert JSON String To JSON Object
		request = json.loads(message)
		func = functions.get(route[request['type']])
		
		# Send Response
		func(request, self)
	
############################################################
# Decorator To Make Route Functions Available TO JSON Call #
############################################################

def add_to_json_function(func):
	functions[func.__name__] = func	
	return func	

@add_to_json_function
@gen.coroutine
def adminRefresh(request, socket):
	for s in sockets:
		s.write_message({
			"type" : "refresh"
		})

@add_to_json_function
@gen.coroutine
def deleteGame(request, socket):
	Games = socket.settings['db'].game
	g = yield Games.remove({"_id" : ObjectId(request['gameid'])})

	socket.write_message({
		"type" : "alert",
		"msg" : "Game Deleted"
	})


@add_to_json_function
@gen.coroutine
def redirect(request, socket):
	for s in sockets:
		if str(s.username) == str(request['user']):
			s.write_message({
				"type" : "redirect",
				"ip" : request['ip']
			});

@add_to_json_function
@gen.coroutine
def isOnline(request, socket):
	isOnline = False
	for s in sockets:
		if str(s.username) == str(request['user']):
			isOnline = True
			socket.write_message({
				"type" : "onlinestatus",
				"user" : request['user'],
				"status" : "online"
			});
	if not isOnline:
		socket.write_message({
			"type" : "onlinestatus",
			"user" : request['user'],
			"status" : "offline"
		});	
	

@add_to_json_function
@gen.coroutine
def gameReport(request, socket):
	Participants = socket.settings['db'].participants
	Games = socket.settings['db'].game

	report =  eval(request['report'])
	report.pop('_id', None)

	report['type'] = "gameReport"
	u1 = yield Participants.find_one({"username":report['user1']})
	u2 = yield Participants.find_one({"username":report['user2']})
	report['user2'] = u2['_id']
	report['user1'] = u1['_id']
	Games.insert(report)
	for s in admin:
		s.write_message(report)

@add_to_json_function
@gen.coroutine
def illegal(request, socket):
	Participants = socket.settings['db'].participants
	Games = socket.settings['db'].game

	for s in sockets:
		if str(s.oid) == str(request['recipient']):
			s.write_message(request)

	p = yield Participants.find_one({"_id" : ObjectId(socket.oid) })
	games = p['games']
	games.reverse()
	for g in games:
		if g['status'] == "pending" :
			gameid = g['gameid']
			break

	gs = yield Games.find_one({"_id":ObjectId(gameid)})

	if gs is not None:
		move = '_' + request['by'] + '( ' + request['from'] + ' - ' + request['to'] + ' )_'
		if request['count'] >= 2:
			if request['by'] == 'b':
				winner = 'white'
			else:
				winner = 'black'

			if winner == "white" :
				Participants.update( {"_id" : ObjectId(gs['user1'])}, 
					{
						"$inc" : {
							"points" : 1
						}			
					}
				)

			elif winner == "black":
				Participants.update( { "_id" : ObjectId(gs['user2'])},
					{
						"$inc" : {
							"points" : 1
						}
					}
				)
			else:
				pass

			Games.update({
				"_id" : ObjectId(gameid)
			}, {
				"$set" : { 
					"status" : "ended",
					"winner" : winner,
					"user1time" : request['white_time'],
					"user2time" : request['black_time'],
					"billegal" : request['billegal'],
					"willegal" : request['willegal']
				}, 
				"$addToSet" : {
					"moves" : {
						request['by'] : move
					}
				}
			})
		else:
			Games.update({
				"_id" : ObjectId(gameid)
			}, {
				"$set" : { 
					"billegal" : request['billegal'],
					"willegal" : request['willegal']
				}, 
				"$addToSet" : {
					"moves" : {
						request['by'] : move
					}
				}		
			})
	

@add_to_json_function
@gen.coroutine
def clockSync( request, socket ):
	for s in sockets:
		if str(s.oid) == str(request['recipient']):
			s.write_message( request )
			socket.write_message( request )

@add_to_json_function
@gen.coroutine
def gameResult(request, socket):
	Participants = socket.settings['db'].participants
	Games = socket.settings['db'].game

	p = yield Participants.find_one({"_id" : ObjectId(socket.oid) })
	
	games = p['games']
	games.reverse()
	for g in games:
		if g['status'] == "pending" :
			gameid = g['gameid']
			break

	gs = yield Games.find_one({"_id" : ObjectId(gameid) })
	
	if request['result'] == 'pending':
		Games.update({
			"_id" : ObjectId(gameid)
		}, {
			"$set" : { 
				"user1time" : request['whitetimer'],
				"user2time" : request['blacktimer']
			}		
		})
	else:
		if request['result'] == "white" :
			Participants.update( {"_id" : ObjectId(gs['user1'])}, 
				{
					"$inc" : {
						"points" : 1
					}			
				}
			)

		elif request['result'] == "black":
			Participants.update( { "_id" : ObjectId(gs['user2'])},
				{
					"$inc" : {
						"points" : 1
					}
				}
			)

		else:
			Participants.update( { "_id" : ObjectId(gs['user1'])},
				{
					"$inc" : {
						"points" : 0.5
					}
				}
			)
			Participants.update( { "_id" : ObjectId(gs['user2'])},
				{
					"$inc" : {
						"points" : 0.5
					}
				}
			)
	
		Games.update({
			"_id" : ObjectId(gameid)
		}, {
			"$set" : { 
				"status" : "ended",
				"winner" : request['result'],
				"user1time" : request['whitetimer'],
				"user2time" : request['blacktimer']
			}		
		})
	

	
@add_to_json_function
@gen.coroutine
def syncMove(request, socket):
	Participants = socket.settings['db'].participants
	Games = socket.settings['db'].game
	if request['by'] == "black" :
		by = 'b'
	else:
		by = 'w'
	move = by+'( ' + request['from'] + ' - ' + request['to'] + ' )'
	p = yield Participants.find_one({"_id" : ObjectId(request['recipient']) })
	
	games = p['games']
	games.reverse()
	for g in games:
		if g['status'] == "pending" :
			gameid = g['gameid']
			break

	Games.update({
		"_id" : ObjectId(gameid)
	}, { 
		"$set" : { 
			"fen" : request['fen'],
			"user1time" : request['wtime'],
			"user2time" : request['btime'],
			"turn" : request['turn']
		}, 
		"$addToSet" : {
			"moves" : {
				by : move
			}
		}
	})

	user1 = socket
	
	for s in sockets:
		if str(s.oid) == str(request['recipient']):
			user2 = s
			s.write_message( request )

	if request['end'] == 0:
		response = { 
			"type" : "syncTime",
			"turn" : request['turn']
		}
	
		user1.write_message(response)
		user2.write_message(response)
	
@add_to_json_function
@gen.coroutine
def startGame(request, socket):
	Participants = socket.settings['db'].participants
	Games = socket.settings['db'].game
	try:
		game = yield Games.find_one({ "_id" : ObjectId(request['gameid']) })
		if game is None:
			print 'Game Not Found'
		else:
			white = yield Participants.find_one({ "_id" : ObjectId(game['user1']) })
			black = yield Participants.find_one({ "_id" : ObjectId(game['user2']) })

			for i in [ObjectId(game['user1']), ObjectId(game['user2'])]:
				w = yield Participants.update({
						"_id" : i
					}, {
						"$addToSet" : { 
							"games" : {
								"gameid" : str(game['_id']),
								"status" : "pending", # Deprecated
								"win" : "-1"		# Deprecated
							}
						}
					})
			
			if white is not None and black is not None:
				response = {
					"type" : "startGame",
					"game" : { 
						"id" : str(game['_id']),
						"white" : {
							"id" : str(white['_id']),
							"key" : str(white['key']),
							"name" : white['name']
						},
						"black" : {
							"id" : str(black['_id']),
							"key" : str(black['key']),
							"name" : black['name']
						},
						"fen" : game['fen']
					}
				}

				count = 0 
				for s in sockets:
					if str(s.oid) == str(white['_id']) or str(s.oid) == str(black['_id']):
						print 'written'
						count = count + 1
						s.write_message(response)
				if count >= 2:
					socket.write_message({
						"type" : "alert",
						"msg" : 'Game started between ' + white['username'] + ' Vs ' + black['username']
					})
				else:
					socket.write_message({
						"type" : "alert",
						"msg" : 'Failed to start game between ' + white['username'] + ' Vs ' + black['username']
					})
			else:	
				print 'Participant is not available'				
	except:
		print sys.exc_info()[0]	
