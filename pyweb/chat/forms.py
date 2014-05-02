from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import ChatUserProfile, Conversation, Message

# class ChatUserProfileForm(ModelForm):
# 	class Meta:
# 		model = ChatUserProfile
# 		fields = ('user',)


class UserForm(ModelForm):
	class Meta:
		model = User
		fields = ('id', 'username', 'email', 'password', )
		#'username'

class MessageForm(ModelForm):
	class Meta:
		model = Message
		fields = ('message_id', 'text', 'timestamp', 'sender', )
		# fields = '__all__'

class ConversationForm(ModelForm):
	class Meta:
		model = Conversation
		fields = ('id', 'participants', 'messages', )
		# fields = 