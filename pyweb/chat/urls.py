from django.conf.urls import patterns, url

from chat.views import UserCreateView, UserRestView, MessageCreateView, MessageRestView, ConversationCreateView, ConversationRestView

urlpatterns = patterns('',
    url(r'^msg/$', MessageCreateView.as_view()),
	url(r'^msg/(?P<pk>\d+)/$', MessageRestView.as_view()),
    url(r'^conv/$', ConversationCreateView.as_view()),
	url(r'^conv/(?P<pk>\d+)/$', ConversationRestView.as_view()),
    url(r'^usr/$', UserCreateView.as_view()),
	url(r'^usr/(?P<pk>\d+)/$', UserRestView.as_view())
)