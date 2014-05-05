from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Profile, Conversation, Message

class ProfileCreateForm(ModelForm):
	class Meta:
		model = Profile
		fields = ('id', 'user',)

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		fields = ('user',)

class UserCreateForm(ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'password', )

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