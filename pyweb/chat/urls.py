from django.conf.urls import patterns, url, include

from .views import UserCreateView, UserRestView, MessageCreateView, MessageRestView, \
	ConversationCreateView, ConversationRestView, ProfileCreateView, ProfileRestView

api_urlpatterns = patterns('',
	# Message REST URLs
	url(r'^message/$', MessageCreateView.as_view(), name='message-create'),
	url(r'^message/(?P<id>\w+)/$', MessageRestView.as_view(), name='message-rest'),
	# Conversation REST URLs
    url(r'^conversation/$', ConversationCreateView.as_view(), name='conversation-create'),
	url(r'^conversation/(?P<id>\w+)/$', ConversationRestView.as_view(), name='conversation-rest'),
	# User REST URLs
    url(r'^user/$', UserCreateView.as_view(), name='user-create'),
	url(r'^user/(?P<id>\d+)/$', UserRestView.as_view(), name='user-rest'),
	#Profile REST URLs
	url(r'^user/(?P<username>\w+)/profile/$', ProfileCreateView.as_view(), name='profile-create'),
	url(r'^user/(?P<username>\w+)/profile/(?P<id>\d+)/$', ProfileRestView.as_view(), name='profile-rest')
)

urlpatterns = patterns('chat.views',
	# Application Index Page
	url(r'^$', 'application_index', name='appindex'),
	url(r'^api/', include(api_urlpatterns, namespace='api')),
)