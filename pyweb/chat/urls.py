from django.conf.urls import patterns, url, include

from .views import UserAuthenticateView, UserCreateView, UserRestView, MessageCreateView, \
	MessageRestView, ConversationCreateView, ConversationRestView, \
	ProfileRestView
	


api_urlpatterns = patterns('',
	# Conversation REST URLs
    url(r'^conversation/$', ConversationCreateView.as_view(), name='conversation-create'),
	url(r'^conversation/(?P<pk>\w+)/$', ConversationRestView.as_view(),
		name='conversation-rest'),

	# Message REST URLs
	url(r'^conversation/(?P<cpk>\w+)/message/(?P<pk>\w+)/$', MessageRestView.as_view(),
		name='message-rest'),
	url(r'^conversation/(?P<cpk>\w+)/message/$', MessageCreateView.as_view(),
		name='message-create'),

	# User REST URLs
	url(r'^user/(?P<pk>\d+)/$', UserRestView.as_view(), name='user-rest'),
    url(r'^user/$', UserCreateView.as_view(), name='user-create'),

	# User Authentication View
	url(r'^login/', UserAuthenticateView.as_view(), name='user-authenticate'),

	# Profile REST URLs
	url(r'^user/(?P<pk>\w+)/profile/$', ProfileRestView.as_view(), name='profile-rest'),

	url(r'^test/(?P<pk>\d+)$', ProfileRestView.as_view(), name='login-test')
)

urlpatterns = patterns('chat.views',
	# Application Index Page
	url(r'^$', 'application_index', name='appindex'),
	url(r'^api/', include(api_urlpatterns, namespace='api')),
)