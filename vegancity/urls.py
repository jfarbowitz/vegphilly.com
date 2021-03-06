# Copyright (C) 2012 Steve Lamb

# This file is part of Vegancity.

# Vegancity is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Vegancity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Vegancity.  If not, see <http://www.gnu.org/licenses/>.

from django.core.urlresolvers import reverse
from django.conf.urls import patterns, include, url
from django.contrib import admin
from settings import INSTALLED_APPS
from vegancity import models, views
from .api import build_api

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^api/', include(build_api().urls)),

    url(r'^admin/pending_approval/$', 'vegancity.admin_views.pending_approval', name="pending_approval"),
    url(r'^admin/pending_approval/count/$', 'vegancity.admin_views.pending_approval_count', name="pending_approval_count"),
    url(r'^admin/mailing_list/$', 'vegancity.admin_views.mailing_list', name="mailing_list"),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', views.home, name='home'),
    url(r'^vendors/$', views.vendors, name="vendors"),
    url(r'^vendors/add/$', views.new_vendor, name="new_vendor"),
    url(r'^vendors/add/thanks/$', views.VendorThanksView.as_view(), name="vendor_thanks"),
    url(r'^vendors/review/(?P<vendor_id>\d+)/$', views.new_review, name="new_review"),
    url(r'^vendors/(?P<pk>\d+)(-[\w\d]+)*/$', views.VendorDetailView.as_view(), name="vendor_detail"),
    url(r'^about/$', views.AboutView.as_view(), name='about'),
    url(r'^privacy/$', views.PrivacyView.as_view(), name='privacy'),
    url(r'^vendors/review/(?P<pk>\d+)/thanks/$', views.ReviewThanksView.as_view(), name="review_thanks"),

    url(r'^accounts/login/$',  'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page' : '/'},  name='logout'),
    url(r'^accounts/register/$', 'vegancity.views.register', name='register'),
    url(r'^accounts/register/thanks/$', views.RegisterThanksView.as_view(), name='register_thanks'),
    url(r'^accounts/password/change/$', 'vegancity.views.password_change', name='password_change'),
    url(r'^accounts/profile/$', 'vegancity.views.user_profile', { 'username': None }, name='my_account'),
    url(r'^accounts/profile/edit/$', 'vegancity.views.account_edit', name='account_edit'),

    url(r'^users/(?P<username>[a-zA-Z0-9_@.+-]+)/$', 'vegancity.views.user_profile', name='user_profile'),
)
