from django.conf.urls import patterns, url, include

from .views import UserCreateView, UserRestView, \
	MessageCreateView, MessageRestView, ConversationCreateView, ConversationRestView

api_urlpatterns = patterns('',
	# Message REST URLs
	url(r'^msg/$', MessageCreateView.as_view(), name='message-create'),
	url(r'^msg/(?P<pk>\d+)/$', MessageRestView.as_view(), name='message-rest'),
	# Conversation REST URLs
    url(r'^conv/$', ConversationCreateView.as_view(), name='conversation-create'),
	url(r'^conv/(?P<pk>\d+)/$', ConversationRestView.as_view(), name='conversation-rest'),
	# Profile REST URLs
    url(r'^usr/$', UserCreateView.as_view(), name='profile-create'),
	url(r'^usr/(?P<pk>\d+)/$', UserRestView.as_view(), name='profile-rest')
)

urlpatterns = patterns('chat.views',
	# Application Index Page
	url(r'^$', 'application_index', name='appindex'),
	url(r'^api/', include(api_urlpatterns, namespace='api')),
)