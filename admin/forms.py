import re
from django import forms
from chess.models import *

class installForm(forms.Form):
	username = forms.CharField(max_length=20, min_length=5, error_messages={'required':'Username is required'})
	password = forms.CharField(max_length=20, min_length=5, error_messages={'required':'Password is required'})

	def clean_username(self):
		r = re.compile('[a-z]+')
		username = self.cleaned_data.get('username')
		if not r.match(username):
			raise forms.ValidationError('Username is not valid')
		return username

class loginForm(forms.Form):
	username = forms.CharField(max_length=20, min_length=5, error_messages={'required':'Username is required'})
	password = forms.CharField(max_length=20, min_length=5, error_messages={'required':'Password is required'})
	
	# Check if the 'username' exist
	def clean_username(self):
		username = self.cleaned_data.get('username')
		try:
			self.user = Admin.objects.get(user_name = username)
		except Admin.DoesNotExist:
			raise forms.ValidationError('Username does not exist')	
		return username
		
	def clean(self):
		cleaned_data = super(loginForm, self).clean()
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')
		if username and password:

			if self.user.password != password:
				raise forms.ValidationError('Invalid Username/Password Combination')
		return cleaned_data
