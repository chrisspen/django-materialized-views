#!/usr/bin/python
"""
2012.3.29 CKS
Updates all materialized view models.
"""
import sys
from optparse import make_option

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
import django

from django_materialized_views.models import MaterializedView

def update(**kwargs):
    """
    Iterate over all materilized view models and materializes them.
    """
    reraise = kwargs.get('reraise')
    limit_to_models = map(str.strip, kwargs.get('models', '').split(','))
    for mdl in MaterializedView.__subclasses__():
        n = mdl.__name__
        if limit_to_models and n not in limit_to_models:
            continue
        try:
            print>>sys.stdout, 'Updating materialized view %s...' % str(mdl)
            mdl.materialize(**kwargs)
        except Exception, e:
            if reraise:
                raise
            print>>sys.stderr, 'Error while materializing view %s:' % str(mdl)
            print>>sys.stderr, e

class Command(BaseCommand):
    help = 'Updates all materialized view models.'
    args = ''
    option_list = BaseCommand.option_list + (
        make_option('--do_insert',
            default=True,
            dest='do_insert'),
        make_option('--do_update',
            default=True,
            dest='do_update'),
        make_option('--do_delete',
            default=True,
            dest='do_delete'),
        make_option('--stripe',
            dest='stripe'),
        make_option('--models',
            default='',
            dest='models'),
        make_option('--reraise',
            default=False,
            action='store_true',
            dest='reraise'),
        )

    def handle(self, *args, **options):
        options['do_insert'] = int(options['do_insert'])
        options['do_update'] = int(options['do_update'])
        options['do_delete'] = int(options['do_delete'])
        update(**options)
