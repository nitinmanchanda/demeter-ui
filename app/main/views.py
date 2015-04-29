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
import json

demeter_base_url = "http://localhost:81"

@main.route('/', methods=['GET', 'POST'])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        # session.__setattr__('name', form.name.data)
        # session.__setattr__('known', True)
        form.name.data = ''
        # return redirect(url_for('.index'))
    return render_template('index.html', form=form, name=name)
    # return render_template('index.html',
    #                        form=form, name=session.get('name'),
    #                        known=session.get('known', False),
    #                        current_time=datetime.utcnow())


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
    r = requests.post(demeter_base_url + '/seo/content/add_content', data)

    message = "Error while adding content for " + data['url'] + ". Review the content and other parameters once, contact admin if that doesn't help!"
    
    if json.loads(r.text)['result'] and json.loads(r.text)['result'] == 'Success':
        message = "Content for " + data['url'] + " has been added successfully!"
    
    return render_template('result.html', message=message)

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
