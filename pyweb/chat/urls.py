from django.conf.urls import patterns, url

from chat.views import Old
from chat.views import TestCBVUser

#TODO: clean this up, remove Old, make everything CBV.
urlpatterns = patterns('',
	url(r'^$', Old.index, name='index'),
    # url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    # url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    # url(r'^(?P<question_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^message/', Old.message, name='message'),
	url(r'^user/', Old.user, name='user'),
	url(r'^conversation/', Old.conversation, name='conversation'),
	url(r'^test/(?P<pk>\d+)/$', TestCBVUser.as_view(), name='test') 
)