import uuid, json
import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from .models import ChatUserProfile, Message, Conversation

logger = logging.getLogger(__name__)

class UserRestView(View):
	def get(self, request, *args, **kwargs):
		user = User.objects.get(pk=kwargs['pk'])
		
		#when I try to use json.dumps(user) it gives an error saying its not JSON
		#	serializable
		data = serializers.serialize('json', [user, ])
		logger.info(data)
		#return HttpResponse(json.dumps(model_to_dict(user)), content_type='application/json')
		return HttpResponse(data, content_type='application/json')

	def put(self, request, *args, **kwargs):
		udata = serializers.deserialize(request.body)
		udata.save()
		#what to return here
		return HttpResponse('')

	def delete(self, request, *args, **kwargs):
		pass

	def post(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

class UserCreateView(View):
	def get(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def delete(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def post(self, request, *args, **kwargs):
		pass

class ConversationRestView(View):
	def get(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def delete(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def post(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

class ConversationCreateView(View):
	def get(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def delete(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def post(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

class MessageRestView(View):
	def get(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def delete(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def post(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

class MessageCreateView(View):
	def get(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def put(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def delete(self, request, *args, **kwargs):
		return HttpResponseBadRequest()

	def post(self, request, *args, **kwargs):
		return HttpResponseBadRequest()		







# class LoginRequiredMixin(object):
#     @classmethod
#     def as_view(cls, **initkwargs):
#         view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
#         return login_required(view)

# class TestCBVUser(View):

# 	def get(self, request, *args, **kwargs):
# 		cuser = ChatUserProfile.objects.get(pk=self.kwargs['pk'])
# 		user = User.objects.get(pk=cuser.pk)
# 		# cuser.user = serializers.serialize('json', [User.objects.get(pk=cuser.pk), ])
# 		data = serializers.serialize('json', [cuser, ])
# 		print user.username
# 		return HttpResponse(data, content_type='application/json')
# 		# self.object = self.get_object(queryset=ChatUserProfile.objects.all())
# 		# return super(TestCBVUser, self).get(request, *args, **kwargs)

# class Old:
# 	unimplementedStr = "This has yet to be implemented..."
# 	# Create your views here.
# 	@staticmethod
# 	def index(request):
# 		return HttpResponse("Hello, I'm working")


# 	# GET - return user object if valid login data
# 	#	  - include conversation id's
# 	# POST - createuser
# 	@staticmethod
# 	def user(request):
# 		# data = ChatUserProfile()
# 		if request.method == 'GET':
# 			username = str(uuid.uuid4().hex)
# 			#we need to secure this, salt it or w/e
# 			password = 'testPassword'
# 			email = 'testEmail@email.com'
# 			cuser = User.objects.create_user(username=username, password=password, email=email)
# 			cuser.save()
# 			data = serializers.serialize('json', [cuser, ])
# 			# data = serializers.serialize('json', cuser)
# 			return HttpResponse(data, content_type='application/json')
# 		elif request.method == 'POST':
# 			return HttpResponse(unimplementedStr)

# 		return HttpResponse(unimplementedStr)

# 	#POST - send message
# 	@staticmethod
# 	def message(request):

# 		return HttpResponse(unimplementedStr)	

# 	#GET - request a list of conversations
# 	#POST - start a conversation
# 	#
# 	@staticmethod
# 	def conversation(request):
# 		return HttpResponse(unimplementedStr)

