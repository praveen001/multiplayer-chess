from django.conf.urls import patterns, include, url
from views import login, install, home, addParticipant, viewParticipants, customMatch, editParticipant, logOut, gameList

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', login),
	url(r'^install/$', install),
	url(r'^home/$', home),
	url(r'^add-participant/$', addParticipant),
	url(r'^view-participants/$', viewParticipants),
	url(r'^edit-participant/([a-zA-Z0-9]+)/$', editParticipant),
	url(r'^custom-match/$', customMatch),
	url(r'^logout/$', logOut),
	url(r'^game-list/$', gameList),

    # Examples:
    # url(r'^$', 'languageexplorer.views.home', name='home'),
    # url(r'^languageexplorer/', include('languageexplorer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
