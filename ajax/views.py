from django.shortcuts import *
import json, sys
import string, random
from chess.models import Participants, Game

def getRandomHash(size=26, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def editParticipant(request, *args, **kwargs):
	try:
		if request.body and request.is_ajax:
			data = eval(request.body)

			try:
				u = Participants.objects.get(id = args[0])
			except Participants.DoesNotExist:
				response = HttpResponse(json.dumps({'error':'Bad Request'}))
			else:
				u.username = data[0]['value']			
				u.name = data[1]['value']
				u.password = data[2]['value']
				u.email = data[3]['value']
				u.college = data[4]['value']
				u.rating = data[5]['value']
				u.cround = data[6]['value']
				u.eliminated = data[7]['value']
				u.points = float(data[8]['value'])
				u.save()
				response = HttpResponse(json.dumps({'success':'Saved'}))
		else:
			response = HttpResponse(json.dumps({'error':'Unknown Request'}))
	except:
		print sys.exc_info()[0]
		response = HttpResponse(json.dumps({'error':'Unknown Request'}))
	return response


def addParticipant(request):
	try:
		if request.body and request.is_ajax:
			data = eval(request.body)

			try:
				u = Participants.objects.get(username = data[0]['value'])
				return HttpResponse(json.dumps({'error' : 'Username exists'}))
			except Participants.DoesNotExist:
				if len(data[0]['value']) != 0 and len(data[1]['value']) != 0 and len(data[2]['value']) != 0:
					new_participant = Participants()
					new_participant.username = data[0]['value']
					new_participant.name = data[1]['value']
					new_participant.password = data[2]['value']
					new_participant.key = getRandomHash()
					# if mail id is provided
					if len(data[3]['value']) != 0:
						new_participant.email = data[3]['value']
					# if school name is provided
					if len(data[4]['value']) != 0:
						new_participant.college = data[4]['value']
					# if rating is provided
					if len(data[5]['value']) != 0:
						new_participant.rating = data[5]['value']
					# if round is provided
					if len(data[6]['value']) != 0:
						new_participant.cround = data[6]['value']
					# if eliminated
					if len(data[7]['value']) != 0:
						new_participant.eliminated = data[7]['value']
					# if points is provided
					if len(data[8]['value']) != 0:
						new_participant.points = data[8]['value']
					new_participant.save()
					return HttpResponse(json.dumps({'success' : 'User created'}))
				else:
					# Registration Error
					return HttpResponse(json.dumps({'error' : 'Required fields can\'t be blank'}))		
		else:
			return HttpResponse(json.dumps({'error':'Bad Request'}))
	except:
		print sys.exc_info()[0]
		return HttpResponse(json.dumps({'error' : 'Internal Error'}))

def startGame(request):
	try:
		if request.body and request.is_ajax:
			data = json.loads(request.body)
			try:
				u1 = Participants.objects.get(username = data[0]['value'])
				u2 = Participants.objects.get(username = data[1]['value'])
			except Participants.DoesNotExist:
				raise Http404
			else:
				g = Game()
				g.user1 = str(u1.id)
				g.user2 = str(u2.id)
				g.cround = str(data[2]['value'])
				g.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
				g.status = "pending"
				# Make Count Down Values Here
				g.save()
				
				response = HttpResponse(json.dumps({ 'gameid' : str(g.id), 'route' : 'socket', 'type' : 'startGame' }))	
				#else:
				#	response = HttpResponse(json.dumps({ 'gameid' : str(g.id), 'route' : 'socket', 'type' : 'startGameNoTime' }))	
		else:
			raise Http404
	except:
		print sys.exc_info()[0]
		response = HttpResponse(json.dumps({'error':'Internal Error'}))
	return response
