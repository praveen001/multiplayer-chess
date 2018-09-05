from django import template
from chess.models import *
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
import base64
import struct
from django.core import serializers
from django.utils import simplejson

client = MongoClient()
fs = GridFS(client.chess)

register = template.Library()



@register.filter(name = 'getNameById')
def getNameById(value):
	try:
		u = Participants.objects.get(id = value)
	except Participants.DoesNotExist:
		return value
	else:
		return u.name

@register.filter(name = 'parse')
def parse(value):
	try:
		u = Participants.objects.get(id = value.user1)
		value.user1 = str(u.username)
		v = Participants.objects.get(id = value.user2)
		value.user2 = str(v.username)
		return value.to_json()
	except Participants.DoesNotExist:
		return value.to_json()
	

@register.filter(name = 'getRatingById')
def getRatingById(value):
	try:
		u = Participants.objects.get(id = value)
	except Participants.DoesNotExist:
		return -1
	else:
		return u.rating

@register.filter(name = 'getPointsById')
def getPointsById(value):
	try:
		u = Participants.objects.get(id = value)
	except Participants.DoesNotExist:
		return -1
	else:
		return u.points
