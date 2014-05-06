from django.forms import ModelForm, CharField
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
	verifyPassword = CharField(100)
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'username', 'email', 'password', )

# class UserAuthenticateForm(ModelForm):
# 	class Meta:
# 		model = User
# 		fields = ('username', 'password', )

# 	def clean(self):
# 		cleaned_data = super(self.__class__, self).clean()
# 		username = clean_data.get('username')
# 		password = clean_data.get('password')
# 		user = authenicate(username=username, password=password)
# 		if user is not None:
# 			if user.is_active:
# 				login(request, user)
# 			else:
# 				raise self.ValidationError("User account %s is disabled" % username)
# 		else:
# 			raise self.ValidationError("Invalid username and/or password")
# 		return cleaned_data

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