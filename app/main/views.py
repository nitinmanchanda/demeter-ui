__author__ = 'nitin'

from datetime import datetime
from flask import render_template, session, redirect, url_for
from .import main
from .forms import NameForm
from .. import db
from ..models import User
import urllib2, json, operator
from webargs.core import Arg
from webargs.flaskparser import parser
from flask import request
import requests
import json, collections
import random


api_base_url = "http://localhost:81"


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


###################
# Content Service #
###################
@main.route('/seo/content/add_content')
def add_new_content():
    return render_template('create_content.html', url='add_content/result')


@main.route('/seo/content/add_content/result', methods=['GET', 'POST'])
def add_new_content_result():
    args = {
        'url': Arg(str, required=True),
        'short_description': Arg(str, default=None),
        'content_header': Arg(str, default=None),
        'content': Arg(str, required=True)
    }

    data = parser.parse(args, request)
    r = requests.post(api_base_url + '/seo/content/add_content', data)

    message = "Error while adding content for " + data['url'] + ". Review the content and other parameters once, contact admin if that doesn't help!"
    message_color = "red"

    if json.loads(r.text)['result'] and json.loads(r.text)['result'] == 'Success':
        message = "Content for " + data['url'] + " has been added successfully!"
        message_color = "green"
    
    return render_template('result.html', message=message, message_color=message_color)


################
# Meta Service #
################
@main.route('/seo/meta/add_meta_data')
def add_new_meta():
    return render_template('create_meta.html', url='add_meta_data/result')


@main.route('/seo/meta/add_meta_data/result', methods=['GET', 'POST'])
def add_new_meta_result():
    args = {
        'page_type': Arg(str, required=True),
        'url': Arg(str, default=None),
        'page_param': Arg(str, default=None),
        'h1': Arg(str, default=None),
        'meta_title': Arg(str, default=None),
        'meta_description': Arg(str, default=None),
        'meta_keywords': Arg(str, default=None),
        'og_tags': Arg(str, default='{}'),
        'twitter_cards': Arg(str, default='{}'),
        'gplus_tags': Arg(str, default='{}')
    }

    data = parser.parse(args, request)

    r = requests.post(api_base_url + '/seo/meta_data/add_meta_data', data)

    message = "Error while adding meta data for " + data['page_type'] + ". Review the content and other parameters once, contact admin if that doesn't help!"
    message_color = "red"

    if json.loads(r.text)['result'] and json.loads(r.text)['result'] == 'Success':
        message = "Meta data for " + data['page_type'] + " has been added successfully!"
        message_color = "green"
    
    return render_template('result.html', message=message, message_color=message_color)


###################
# Keyword Service #
###################
@main.route('/seo/keyword/keywordtool', methods=['GET', 'POST'])
def keywordtool_api():
    apikey = '579a5b85df0459956f0be0875d99083fc0740958'

    args = {
        'keyword': Arg(str, default=None)
    }

    result = None
    sorted_list = None
    data = parser.parse(args, request)
    if data['keyword']:
        api = 'http://api.keywordtool.io/v1/search/google?apikey=%s&country=in&language=en&metrics=true&keyword=%s' % (apikey, data['keyword'])
        r = requests.post(api)
        result = json.loads(r.text)['results']
        sorted_list = sorted(result)
    return render_template('keyword_data.html', data=result, sorted_list=sorted_list)


@main.route('/seo/keyword/google_suggest', methods=['GET', 'POST'])
def google_suggest_api():
    google_suggest_domain = [
        'http://google.com/complete/search',
        'http://suggestqueries.google.com/complete/search',
        'http://clients1.google.com/complete/search'
    ]

    args = {
        'keyword': Arg(str, default=None)
    }

    result = None
    data = parser.parse(args, request)
    keyword = data['keyword']

    if keyword:
        domain_picked = random.choice(google_suggest_domain)
        api = '%s?client=firefox&q=%s&hl=en&gl=in' % (domain_picked, keyword)
        r = requests.get(api)
        result = json.loads(r.text)[1]

    return render_template('google_suggest.html', keyword=keyword, data=result)


##################
# Mapper Service #
##################
@main.route('/seo/mapper/create_custom_landing_page')
def create_custom_landing_page():
    return render_template('create_custom_landing_page.html', url='create_custom_landing_page/result')


@main.route('/seo/mapper/create_custom_landing_page/result', methods=['GET', 'POST'])
def create_custom_landing_page_result():
    args = {
        'url': Arg(str, required=True),
        'existing_url': Arg(str, required=True),
        'h1': Arg(str, default=None),
        'meta_title': Arg(str, default=None),
        'meta_description': Arg(str, default=None),
        'meta_keywords': Arg(str, default=None),
        'content': Arg(str, default=None)
    }

    data = parser.parse(args, request)
    data['page_type'] = 'url'
    existing_url = data['existing_url']
    existing_page_type = 'category'
    area_available = False

    if "http://www.askme.com" in existing_url:
        existing_url = existing_url.replace("http://www.askme.com", "")

    if "/search/" in existing_url:
        existing_page_type = 'search'
        existing_url = existing_url.replace("/search", "")

    if "/in/" in existing_url:
        area_available = True
        existing_url = existing_url.replace("/in", "")        

    uri_values = existing_url.split("/")
    data['city'] = uri_values[1]    
    if existing_page_type == 'search':
        data['search_query'] = uri_values[2]
    else:
        data['category'] = uri_values[2]

    if area_available:
        data['location'] = uri_values[3]

    mapper_processed = False
    meta_processed = False
    content_processed = False

    api_request = requests.post(api_base_url + '/seo/mapper/add_url_data', data)
    if json.loads(api_request.text)['result'] and json.loads(api_request.text)['result'] == 'Success':
        mapper_processed = True

    if data['content'] is not "":
        api_request = requests.post(api_base_url + '/seo/content/add_content', data)
        if json.loads(api_request.text)['result'] and json.loads(api_request.text)['result'] == 'Success':
            content_processed = True
    else:
        content_processed = True

    if data['h1'] is not "" and data['meta_title'] is not "" and data['meta_description'] is not "" and data['meta_keywords'] is not "":
        api_request = requests.post(api_base_url + '/seo/meta_data/add_meta_data', data)
        if json.loads(api_request.text)['result'] and json.loads(api_request.text)['result'] == 'Success':
            meta_processed = True
    else:
        meta_processed = True

    message = "Error while adding data for " + data['url'] + ". Review the content and other parameters once, contact admin if that doesn't help!"
    message_color = "red"

    if mapper_processed and meta_processed and content_processed:
        message = "Data for " + data['url'] + " has been added successfully!"
        message_color = "green"
    
    return render_template('result.html', message=message, message_color=message_color)


#################
# Redis Service #
#################
@main.route('/seo/redis/meta_data')
def meta_data_redis_push():
    r = requests.get(api_base_url + '/seo/meta_data/reload_cache')

    message = "Not able to push meta service data to redis!"
    message_color = "red"

    if json.loads(r.text)['result'] and json.loads(r.text)['result'] == 'Success':
        message = "Meta service data has been pushed to redis successfully!"
        message_color = "green"
    
    return render_template('result.html', message=message, message_color=message_color)


@main.route('/seo/redis/content_data')
def content_data_redis_push():
    r = requests.get(api_base_url + '/seo/content/reload_cache')

    message = "Not able to push content service data to redis!"
    message_color = "red"

    if json.loads(r.text)['result'] and json.loads(r.text)['result'] == 'Success':
        message = "Content service data has been pushed to redis successfully!"
        message_color = "green"
    
    return render_template('result.html', message=message, message_color=message_color)


@main.route('/seo/redis/mapper_data')
def mapper_data_redis_push():
    r = requests.get(api_base_url + '/seo/mapper/reload_cache')

    message = "Not able to push mapper service data to redis!"
    message_color = "red"

    if json.loads(r.text)['result'] and json.loads(r.text)['result'] == 'Success':
        message = "Mapper service data has been pushed to redis successfully!"
        message_color = "green"
    
    return render_template('result.html', message=message, message_color=message_color)


################
# Test Service #
################
@main.route('/test')
def test():
    # url = 'http://search01.production.askme.com:9999/aggregate/askme/place?agg=city&offset=0&size=200'      
    url = 'http://search01.production.askme.com:9999/aggregate/askme/place?agg=city&offset=0'      
    resp = urllib2.urlopen(url)

    my_data = json.load(resp)
    my_data = my_data['results']['city']['buckets']
    my_data = sorted(my_data.items(), key=operator.itemgetter(1), reverse=True)

    my_data = [x[0] for x in my_data]

    # return str(my_data)
    
    # for city, cardinality in my_data.iteritems():
    #     return city + " => " + str(cardinality)

    return render_template('test.html', name='Nitin', data=my_data)
