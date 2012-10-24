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

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

import forms

import models
import itertools
import rank
import tracking

import functools

def vendors(request):
    """Display table level data about vendors.

    If this view has a get param called query, then we trigger
    the search runmode.  Otherwise, we just return all vendors
    in our database.

    Most of the complexity in this view is due to the ordering
    of results.  This view tries to decide what type of search
    the user is executing and display results accordingly."""

    ############################
    ## FILTERS
    ############################

    # get all the tags in the db.  we'll use this multiple.
    # times.
    all_cuisine_tags =  models.CuisineTag.objects.all()
    all_feature_tags = models.FeatureTag.objects.all()
    all_neighborhoods = models.Neighborhood.objects.all()


    # figure out which filters have been checked
    checked_cuisine_filters = [f for f in all_cuisine_tags
               if request.GET.get(f.name)]
    checked_feature_filters = [f for f in all_feature_tags
               if request.GET.get(f.name)]
    checked_neighborhoods = [f for f in all_neighborhoods
               if request.GET.get(f.name)]
    checked_filters = checked_cuisine_filters + checked_feature_filters + checked_neighborhoods



    # Filter the set of vendors that can be displayed
    # based on what is in the checked filters.
    vendors = models.Vendor.approved_objects.all()
    for f in checked_cuisine_filters:
        vendors = vendors.filter(cuisine_tags__id__exact=f.id)
    for f in checked_feature_filters:
        vendors = vendors.filter(feature_tags__id__exact=f.id)
    for f in checked_neighborhoods:
        vendors = vendors.filter(neighborhood__id__exact=f.id)



    # determine which filters can be presented on the page
    # based on whether they apply to any of the remaining
    # vendors
    available_cuisine_filters = [tag for tag in all_cuisine_tags if 
                       tag.vendor_set.filter(id__in=vendors)]
    available_feature_filters = [tag for tag in all_feature_tags if 
                       tag.vendor_set.filter(id__in=vendors)]
    available_neighborhoods = [n for n in all_neighborhoods if 
                       n.vendor_set.filter(id__in=vendors)]


    ############################
    ## SEARCHES
    ############################

    query = request.GET.get('query', '')

    if query:

        # rank the likelihood of different search times
        ranks = rank.get_ranks(query)
        presentation_order = (rank[1] for rank in ranks)

        # log the query in the db
        tracking.log_query(query, ranks)

        # execute searches and store them in a hash
        searches = {
            'name' : models.Vendor.approved_objects.name_search(query, vendors),
            'address' : models.Vendor.approved_objects.address_search(query, vendors),
            'tags' : models.Vendor.approved_objects.tags_search(query, vendors),
            }

        # compute the set of all vendors found in the 3 searches
        # todo - optimize?
        vendors = [vendor for vendor in vendors if vendor in 
                   itertools.chain(searches['name']['vendors'], 
                                   searches['address']['vendors'], 
                                   searches['tags']['vendors'])]

        result_set = map(lambda x: searches[x], presentation_order)
    
    else:
        # There was no search, show em all!
        result_set = [
            {'summary_statement' : 
             "We've got %d food vendors in our database!"
             % vendors.count(), 'vendors' : vendors,}]

    ctx = {
        'vendors' : vendors,
        'result_set' : result_set,
        'query': query,
        'cuisine_filters' : available_cuisine_filters,
        'feature_filters' : available_feature_filters,
        'neighborhoods' : available_neighborhoods,
        'checked_filters' : checked_filters,
        }
    return render_to_response('vegancity/vendors.html', ctx,
                              context_instance=RequestContext(request))



###########################
## data entry views
###########################

def data_entry_manager(request, closed_form, redirect_url, 
                       template_name, form_init={}, ctx={}, apply_author=False):

    if request.method == 'POST':
        form = closed_form(request.POST)
        
        if form.is_valid():
            obj = form.save(commit=False)
            
            if apply_author:
                obj.author = request.user

            if request.user.is_staff:
                if 'approved' in dir(obj):
                    obj.approved = True
            obj.save()
            return HttpResponseRedirect(redirect_url)
        
    else:
        form = closed_form(initial=form_init)

    ctx['form'] = form
    return render_to_response(template_name, ctx,
                              context_instance=RequestContext(request))


def register(request):
    return data_entry_manager(request, forms.VegUserCreationForm, reverse("home"), "vegancity/register.html")

@login_required
def new_vendor(request):
    return data_entry_manager(request, forms.NewVendorForm, reverse("vendors"), "vegancity/new_vendor.html")

@login_required
def new_review(request, vendor_id):
     vendor = models.Vendor.approved_objects.get(id=vendor_id)
     closed_form = functools.partial(forms.NewReviewForm, vendor)
     ctx = {'vendor': vendor}
     
     return data_entry_manager(
         request, closed_form, reverse("vendor_detail", args=[vendor.id]),
         "vegancity/new_review.html", {'vendor':vendor}, ctx, True)
