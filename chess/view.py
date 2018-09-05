# Create your views here.
import string, random, sys
from django.shortcuts import *
from models import *

def getRandomHash(size=26, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def register(request):
	if request.method == 'GET':
		response = render(request, 'register.html')
	elif request.method == 'POST':
		
		try:
			u = Participants.objects.get(username = request.POST.get('username') )
		except Participants.DoesNotExist:
			if len(request.POST.get('username') ) != 0 and len(request.POST.get('name') ) != 0 and len( request.POST.get('password') ) != 0:
				new_participant = Participants()
				new_participant.username = request.POST.get('username')
				new_participant.name = request.POST.get('name')
				new_participant.password = request.POST.get('password')
				new_participant.key = getRandomHash()
	
				# if mail id is provided
				if len(request.POST.get('email')) != 0:
					new_participant.email = request.POST.get('email')

				# if school is provided
				if len(request.POST.get('college')) != 0:
					new_participant.college = request.POST.get('college')
				new_participant.save()
				response = redirect('/')
			else:
				# Registration Error
				response = render( request, 'register.html', {'reg_error' : 'Required fields cant be blank'} )
		else:
			response = render( request, 'register.html', { 'reg_error' : 'Username not available' } )
	return response

def home(request):
	if request.method == 'GET':
		response = render(request, 'home.html')
	elif request.method == 'POST':
		if request.POST.get('username'):# and request.POST.get('password'):
			try:
				p = Participants.objects.get(username = request.POST.get('username'), password = request.POST.get('password') )
			except Participants.DoesNotExist:
				response = render(request, 'home.html', {"error":"Invalid Username/Password Combination" })	
			else:
				# p.key = getRandomHash()
				p.save()
				response = redirect('/game')
				response.set_cookie('userCookie', p.key )
		else:
			response = render(request, 'home.html', {"error":"Required fields can\'t be blank"})
				
	else:
		raise Http404
	return response

def game(request):
	if request.method == "GET":
		if request.COOKIES.get('userCookie'):
			try:
				p = Participants.objects.get(key=request.COOKIES.get('userCookie'))
			except Participants.DoesNotExist:
				response = redirect('/')
			else:
				response = render(request, 'game.html', {"user":p})	
		else:
			response = redirect('/')		
	else:
		raise Http404
	return response

def game2(request):
	if request.method == "GET":
		return render(request, 'trick.html')

def db(request):
	if request.method == "GET":
		for i in range(1, 351):
			new_participant = Participants()
			new_participant.username = "user" + str(i)
			new_participant.name = "user" + str(i)
			new_participant.password = "123"
			new_participant.key = getRandomHash()
			new_participant.save()
		return render(request, 'home.html')
			
