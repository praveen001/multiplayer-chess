from django.conf.urls import patterns, include, url
from view import home, game, register, game2, db

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', home),
	url(r'^game/$', game),
	url(r'^game2/$', game2),
	url(r'^db/$', db),
	url(r'^admin/', include('admin.urls')),
	url(r'^ajax/', include('ajax.urls')),
	url(r'^register/', register),
    # Examples:
    # url(r'^$', 'event.views.home', name='home'),
    # url(r'^event/', include('event.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
