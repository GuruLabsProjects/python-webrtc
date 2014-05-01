from django.conf.urls import patterns, url

from chat import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    # url(r'^$', views.IndexView.as_view(), name='index'),
    # url(r'^(?P<pk>\d+)/$', views.DetailView.as_view(), name='detail'),
    # url(r'^(?P<pk>\d+)/results/$', views.ResultsView.as_view(), name='results'),
    # url(r'^(?P<question_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^message/', views.message, name='message'),
	url(r'^user/', views.user, name='user'),
	url(r'^conversation/', views.conversation, name='conversation')
)