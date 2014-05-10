from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, CharField
from django.contrib.auth.models import User
from .models import Profile, Conversation, Message

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ('id', 'user',)


class UserCreateForm(UserCreationForm):
	'''	Form used to create new user accounts.
	'''
	#Meta class which defines the model that we're working with, and the fields we
	#	care about validating.
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

	html_placeholder_text = {
		'first_name' : 'First Name',
		'last_name' : 'Last Name',
		'username' : 'Username you would like to use to access the site',
		'email' : 'name@domain.com',
		'password1' : 'Please type your password',
		'password2' : 'Please verify your password',
	}

	def __init__(self, *args, **kwargs):
		'''	Initialize form, add placeholder text to HTML widgets
		'''
		# Initialize the form
		super(self.__class__, self).__init__(*args, **kwargs)
		# Add HTML placeholder text to all widgets in the form
		for fname in self.html_placeholder_text.keys():
			field = self.fields.get(fname)
			if hasattr(field, 'widget'):
				if hasattr(field.widget, 'attrs'):
					field.widget.attrs['placeholder'] = self.html_placeholder_text.get(fname)
		# Require all fields in the model
		for fname in self.fields:
			field = self.fields.get(fname)
			if hasattr(field, 'required'): setattr(field, 'required', True)


class UserForm(ModelForm):
	''' Form for validating User update requests.
	'''
	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password', )

class MessageForm(ModelForm):
	''' Form for validating Messages
	'''
	
	class Meta:
		model = Message
		fields = ('text', )

class ConversationCreateForm(ModelForm):
	''' Form for validation the creation of conversation objects
	'''
	class Meta:
		model = Conversation
		fields = ('participants', 'messages', )

	def clean(self):
		''' we want to make sure people don't attempt to get unauthorized access to messages.
		 		So we make sure the conversation getting sent to us has no messages already
			 	in it.  Conversations are created once as an empty conversation.
		'''

		# get the data from the parent clean method
		clean_data = super(self.__class__, self).clean()
		msgs = None
		if 'messages' in clean_data:
			msgs = clean_data['messages']
			# ensure there are no messages
			if len(msgs) != 0:
				raise ValidationError("New conversations cant have old messages.")				
		return clean_data