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


################
# Test Service #
################
@main.route('/test')
def test():
    url = 'http://search01.production.askme.com:9999/aggregate/askme/place?agg=city&offset=0&size=200'      
    resp = urllib2.urlopen(url)

    my_data = json.load(resp)
    my_data = my_data['results']['city']['buckets']
    my_data = sorted(my_data.items(), key=operator.itemgetter(1), reverse=True)

    my_data = [x[0] for x in my_data]

    # return str(my_data)
    
    # for city, cardinality in my_data.iteritems():
    #     return city + " => " + str(cardinality)

    return render_template('test.html', name='Nitin', data=my_data)
