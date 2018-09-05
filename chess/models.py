from django.db import models
import datetime
from mongoengine import *
connect('chess', host='127.0.0.1', port=27017)

class Admin(Document):
	user_name = StringField(max_length = 20)
	password = StringField(max_length = 20)
	key = StringField(max_length = 26)

class Participants(Document):
	name = StringField(max_length = 20)
	email = StringField(max_length = 100)
	username = StringField(max_length = 20)
	college = StringField(max_length = 60)
	password = StringField(max_length = 20)
	rating = IntField(default = 0)
	cround = IntField(default = 1)
	points = FloatField(default = 0)
	eliminated = IntField(default = 0)
	key = StringField(max_length = 26)
	games = ListField()

class Game(Document):
	user1 = StringField(max_length=40)
	user2 = StringField(max_length=40)
	fen = StringField(max_length=100)
	user1time = IntField(default=900)
	user2time = IntField(default=900)
	status = StringField(max_length=15) #// pending //draw //black //white
	billegal = IntField(default=0)
	willegal = IntField(default=0)
	winner = StringField(max_length=15)
	turn = StringField(max_length=6, default="w")
	cround = IntField(default=0)
	moves = ListField()

