import itertools
import logging
import urllib.parse

from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse, HttpRequest, HttpResponseBadRequest
from search_api import search_and_evaluate

#import capnp
#capnp.remove_import_hook()
#regex_shop_capnp = capnp.load('regex_shop.capnp')

logging.basicConfig()
logger = logging.getLogger(__name__)

import os
from jinja2 import Environment, FileSystemLoader
from django.http import StreamingHttpResponse


def jinja_generate_with_template(template_filename, context):
    template_dir = os.path.dirname(os.path.abspath(__file__)) + '/templates/'

    j2_env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, autoescape=True)
    j2_template = j2_env.get_template(template_filename)
    j2_generator = j2_template.generate(context)

    return j2_generator


def _get_url(keywords, regex_query_string, expression_string):
    return 'http://127.0.0.1:8888/?' + urllib.parse.urlencode(
        {'q': keywords, 'regex': regex_query_string, 'expression': expression_string})

regex_snippets = {
    'number' : r'\p{Nd}+\.?\p{Nd}*'
}

def main(request: HttpRequest):
    context = {}
    keywords = request.GET.get('q')
    regex = request.GET.get('regex')
    expression = request.GET.get('expression')
    if keywords and regex and expression:
        context['search_results'] = search_and_evaluate(keywords, regex, expression)
    else:
        context['search_results'] = []
        context['sample_queries'] = (
            _get_url('solar panel', r'(?P<watts>\p{Nd}+)\p{Z}*(?:w|watts?)(?:\P{L}|\z)', 'price/float(watts)'),
            _get_url('hybrid battery', r'(?P<amp_hours>\p{Nd}+)\p{Z}*(?:ah|amp ?-?hours?)(?:\P{L}|\z)','price/float(amp_hours)'),
            _get_url('hard drive', r'(?P<tb>' + regex_snippets['number'] + r')\p{Z}*(?:tb|tib|terabytes?)(?:\P{L}|\z)','price/(float(tb))'),
            # _get_url('hard drive', r'(?P<tb>\p{Nd}+(?:\.{Nd}+)?)\p{Z}*(?:tb|tib|terabytes?)(?:\P{L}|\z)','price/(float(tb))'),
            _get_url('sd card', r'(?P<gb>\p{Nd}+)\p{Z}*(?:gb|gib|gigabytes?)(?:\P{L}|\z)','price/float(gb)'),
            _get_url('server', r'(?P<ram_gb>\p{Nd}+)\p{Z}*(?:gb|gib|gigabytes?)\p{Z}+ram', 'price/float(ram_gb)'),
            _get_url('air pump', r'(?P<gph>\p{Nd}+)\p{Z}*(?:gph)(?:\P{L}|\z)', 'price/float(gph)'),
            _get_url('food grade tubing', r'(?P<ft>\p{Nd}+)\p{Z}*(?:ft|foot|feet?)(?:\P{L}|\z)', 'price/float(ft)'),
            _get_url('led', r'(?P<watts>\p{Nd}+)\p{Z}*(?:w|watts?)(?:\P{L}|\z)', 'price/float(watts)'),
            _get_url('motor', r'(?P<watts>\p{Nd}+)\p{Z}*(?:w|watts?)(?:\P{L}|\z)', 'price/float(watts)'),
            _get_url('motor', r'(?P<horsepower>\p{Nd}+)\p{Z}*(?:hp|horsepower?)(?:\P{L}|\z)', 'price/float(horsepower)'),
            # search('wifi', r'(?P<mbps>\p{Nd}+)\p{Z}*(?:mbps?)(?:\P{L}|\z)', 'price/float(mbps)'),
            # search('1080p camera', r'', 'price'),
        )

    # def debug_gen(g):
    #     for item in g:
    #         logger.warning(item)
    #         yield item
    return StreamingHttpResponse(jinja_generate_with_template("website/jinja2/main.html", context))
