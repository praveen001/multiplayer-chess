# Create your views here.
import string, random, sys
from django.shortcuts import *
from forms import installForm, loginForm
from chess.models import *


def adminOnly(func):
	def isAdmin(request, *args, **kwargs):
		if request.COOKIES.get('adminCookie'):
			try:
				a = Admin.objects.get(key = request.COOKIES.get('adminCookie'))
			except Admin.DoesNotExist:
				return redirect('/admin/')
			else:
				return func(request, *args, **kwargs)
		else:
			return redirect('/admin/')

	return isAdmin

def noAdmin(func):
	def isAdmin(request, *args, **kwargs):
		if request.COOKIES.get('adminCookie'):
			try:
				a = Admin.objects.get(key = request.COOKIES.get('adminCookie'))
			except Admin.DoesNotExist:
				return func(request, *args, **kwargs)
			else:
				return redirect('/admin/home/')
		else:
			return func(request, *args, **kwargs)

	return isAdmin

def getRandomHash(size=26, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

@noAdmin
def login(request):
	if request.method == 'GET':
		response = render(request, 'admin/login.html')
	else:
		form = loginForm(request.POST)
		if form.is_valid():
			key = form.user.key
			response = redirect('/admin/home/')
			response.set_cookie('adminCookie', key )
		else:
			response = render(request, 'admin/login.html', {'data':request.POST, 'form':form})
	return response

@noAdmin
def install(request):
	if request.method == 'GET':
		try:
			a = Admin.objects.all()
		except Admin.DoesNotExist:
			response = render(request, 'admin/install.html')			
		else:
			response = render(request, 'admin/install.html')

	else:
		form = installForm(request.POST)
		if form.is_valid():
			a = Admin(
					user_name = form.cleaned_data.get('username'), 
					password = form.cleaned_data.get('password'),
					key = getRandomHash()
				)
			a.save()
			response = redirect('/admin/')
		else:
			response = render(request, 'admin/install.html', { 'data' : request.POST, 'form' : form })
	return response
	

@adminOnly
def home(request):
	participants = Participants.objects.all()
	return render(request, 'admin/home.html', { 'participants':participants } )

@adminOnly
def addParticipant(request):
	return render(request, 'admin/add-participant.html')

@adminOnly
def viewParticipants(request):
	participants = Participants.objects.all().order_by('college')
	return render(request, 'admin/view-participants.html', { 'participants':participants })

@adminOnly
def editParticipant(request, *args, **kwargs):
	try:
		participant = Participants.objects.get(id = args[0])
	except Participants.DoesNotExist:
		raise Http404
	else:
		return render(request, 'admin/edit-participant.html', { 'participant': participant })

@adminOnly
def customMatch(request):
	return render(request,'admin/custom-match.html')

@adminOnly
def logOut(request):
	key = getRandomHash()
	response = redirect('/admin/')
	response.set_cookie('adminCookie', key )
	return response

@adminOnly
def gameList(request):
	if request.method == "GET":
		return render(request, 'admin/game-list.html')
	if request.method == "POST":
		try:
			games = Game.objects(cround = request.POST.get('roundno', 0))
			return render(request, 'admin/game-list.html', { 'games': games })
		except Game.DoesNotExist:
			return render(request, 'admin/game-list.html')
		
	
