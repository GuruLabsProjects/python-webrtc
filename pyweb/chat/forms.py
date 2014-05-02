from django.forms import ModelForm
from .models import ChatUserProfile, Conversation, Message

class ChatUserProfileForm(ModelForm):
	class Meta:
		model = ChatUserProfile
		fields = ['user']

class MessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ['message_id', 'text', 'timestamp', 'sender']

class ConversationForm(ModelForm):
	class Meta:
		model = Conversation
		fields = ['participants', 'messages']