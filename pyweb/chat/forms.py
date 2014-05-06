from django.core.exceptions import ValidationError
from django.forms import ModelForm, CharField
from django.contrib.auth.models import User
from .models import Profile, Conversation, Message

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ('id', 'user',)

class UserCreateForm(ModelForm):
	verify_password = CharField(256)
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'password', )

	def clean(self):
		cleanedData = super(self.__class__, self).clean()
		if cleanedData.get('password') != cleanedData.get('verify_password'):
			raise ValidationError("The supplied passwords don't match")
		return cleanedData

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password', )

class MessageCreateForm(ModelForm):
	class Meta:
		model = Message
		fields = ('text', 'timestamp', 'sender', )

class MessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ('id', 'text', 'timestamp', 'sender', )

class ConversationCreateForm(ModelForm):
	class Meta:
		model = Conversation
		fields = ('participants', 'messages', )

class ConversationForm(ModelForm):
	class Meta:
		model = Conversation
		fields = ('id', 'participants', 'messages', )