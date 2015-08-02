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
from HWCMS.views import current_datetime,hours_ahead,index_page,file_show,rule_generate,file_upload,send_message,file_delete,JumpToIndex,file_upload_for_detection
from HWCMS_V1 import settings
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^time/$', current_datetime),
    (r'^time/plus/(\d{1,2})/$', hours_ahead),
    url(r'^index/uploadedfiles',file_upload,name='file_upload'),
    url(r'^index/$',index_page),
    url(r'^index/$',index_page,name="JumpToIndex"),

    url(r'^index_filedeleted/(\d)/$',file_delete,name='file_delete'),
    url(r'^index/(\d)/$',file_show,name='file_show'),
    url(r'^index/rule_show/$',file_upload_for_detection,name='file_upload_for_detection'),
    url(r'^rule_generate/$',rule_generate,name='rule_generate'),
    url(r'^rule_generate/$',rule_generate,name='rule_generate2'),

    ('^send_message/$', send_message),


)
#
if settings.DEBUG:
    urlpatterns += patterns('',
   (r'^static/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': settings.STATIC_ROOT}),
    )