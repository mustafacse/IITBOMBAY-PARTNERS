"""IITBOMBAYX_PARTNERS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('SIP.urls'), name = "SIP"),
    url(r'^logout/$', 'SIP.views.logout'),
     # If user is not login it will redirect to login page
    url(r'^forgot_pass/$', 'SIP.views.forgot_pass'),
    url(r'^resetpass/(?P<emailid>[0-9]+)$', 'SIP.views.resetpass'),
    url(r'^createpass/(?P<emailid>[0-9]+)$', 'SIP.views.createpass'),
    #url(r'^login_success/$','SIP.views.login_success'),
    url(r'^changepass/$','SIP.views.change_pass'),
    url(r'^homepage', 'SIP.views.home'),
   



    
]
