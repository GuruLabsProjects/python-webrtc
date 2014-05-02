import uuid, json, logging, datetime
from django.shortcuts import render
from django.http import HttpResponse
# from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from .models import ChatUserProfile, Message, Conversation
from .forms import UserForm, MessageForm, ConversationForm

logger = logging.getLogger(__name__)

def dateTimeHandler(obj):
	''' Utility function that handles serializing datetime objects that can't otherwise
		be serialized with dumps 
		@useage: jsonRep = json.dumps(someObjWithDateTimeAttribute, default=dateTimeHandler)
	'''
	if isinstance(obj, datetime.datetime) or isinstance(datetime.date):
		obj.isoformat()
	else:
		json.JSONEncoder.default(obj)

class UserRestView(View):
	def get(self, request, *args, **kwargs):
		user = User.objects.get(pk=kwargs['pk'])
		return HttpResponse(json.dumps(model_to_dict(user), default=dateTimeHandler),
			content_type='application/json')

	def put(self, request, *args, **kwargs):
		udata = json.loads(request.body)
		response = {}
		user =  User.objects.get(pk=udata['id'])

		if not user:
			return HttpResponseBadRequest('Invalid id')

		userForm = UserForm(udata, instance=user)
		try:			
			userForm.save()
		except ValueError as errs:
			response['error'] = []
			for err in userForm.errors:
				response['error'].append(str(err))
		return HttpResponse(response)

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