"""HWCMS_V1 URL Configuration

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
from django.conf.urls import patterns, include, url
from HWCMS.views import current_datetime,hours_ahead,file_info,file_info2,file_info3,file_info4,send_message

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^time/$', current_datetime),
    (r'^time/plus/(\d{1,2})/$', hours_ahead),
    url(r'^fileinfo/selectedfiles',file_info4,name='fileinfo4'),
    url(r'^fileinfo/$',file_info),
    url(r'^fileinfo/(\d)/$',file_info2,name='fileinfo2'),
    url(r'^fileinfo3/$',file_info3,name='fileinfo3'),
    ('^send_message/$', send_message),


)
#urlpatterns = [
#    url(r'^admin/', include(admin.site.urls)),
#]
