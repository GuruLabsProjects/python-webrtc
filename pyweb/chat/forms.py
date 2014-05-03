from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Profile, Conversation, Message

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ('user',)

class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'username', 'email', 'password', )

class MessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ('message_id', 'text', 'timestamp', 'sender', )

class ConversationForm(ModelForm):
	class Meta:
		model = Conversation
		fields = ('id', 'participants', 'messages', )