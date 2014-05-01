import uuid
from django.shortcuts import render
from django.http import HttpResponse
from chat.models import ChatUserProfile, Message, Conversation
from django.core import serializers

unimplementedStr = "This has yet to be implemented..."

# Create your views here.
def index(request):
	return HttpResponse("Hello, I'm working")

def user(request):
	# data = ChatUser()
	if request.method == 'GET':
		username = str(uuid.uuid4().hex)
		password = 'testPassword'
		email = 'testEmail@email.com'
		cuser = ChatUser.createUser(username=username, password=password, email=email)
		cuser.save()
		data = serializers.serialize('json', [cuser, ])
		# data = serializers.serialize('json', cuser)
		return HttpResponse(data, content_type='application/json')

	return HttpResponse(unimplementedStr)

def message(request):
	
	return HttpResponse(unimplementedStr)	

def conversation(request):
	return HttpResponse(unimplementedStr)

