#!/usr/bin/python
"""
2012.3.29 CKS
Updates all materialized view models.
"""
import os
import sys
import random
import time
from multiprocessing import Process, Lock, Queue
from optparse import make_option
import traceback
import collections
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import connection
from django.core.management.base import BaseCommand
from django.utils import timezone
import django

try:
    from chroniker.models import Job
except ImportError:
    Job = None

from django_materialized_views.models import (
    MaterializedView, MaterializedViewControl,
)

def is_power_of_two(x):
    return (x & (x - 1)) == 0

def get_control(mdl):
    app_label = None
    if hasattr(mdl, '_meta') and hasattr(mdl._meta, 'app_label'):
        app_label = mdl._meta.app_label
    control, _ = MaterializedViewControl.objects.get_or_create(
        name=mdl.__name__,
        app_label=app_label,
        defaults=dict(
            stripable=mdl.stripable,
            include_in_batch=mdl.include_in_batch,
        ))
    return control

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
#        make_option('--stripe',
#            dest='stripe'),
        make_option('--models',
            default='',
            dest='models'),
        make_option('--list',
            default=False,
            action='store_true'),
        make_option('--reraise',
            default=False,
            action='store_true',
            dest='reraise'),
        make_option('--multi',
            dest='multi',
            default=0,
            help='The number of processes to use. Must be a multiple of 2.'),
        )

    def handle(self, *args, **options):
        options['do_insert'] = int(options['do_insert'])
        options['do_update'] = int(options['do_update'])
        options['do_delete'] = int(options['do_delete'])
        
        self.stripe_counts = {} # {stripe:{current,total}
        self.last_progress_refresh = None
        self.start_times = {} # {key:start_time}
        
        if options['list']:
            for mdl in sorted(MaterializedView.__subclasses__(), key=lambda _: _.__name__):
                control = get_control(mdl)
                print mdl.__name__, mdl._meta.app_label
            return
        
        self.status = None
        self.progress = collections.OrderedDict()
        limit_to_models = map(str.strip, [_ for _ in options.get('models', '').split(',') if _.strip()])
        all_model_names = set(mdl.__name__ for mdl in MaterializedView.__subclasses__())
        for mdl_name in limit_to_models:
            assert mdl_name in all_model_names, 'Invalid model name: %s' % (mdl_name,)
        total_count = len(MaterializedView.__subclasses__())
#        print 'limit_to_models:',limit_to_models
#        return
        multi = int(options['multi'])
        kwargs = options.copy()
        if multi:
            assert multi > 1 and is_power_of_two(multi), \
                "Process count must be greater than 1 and a multiple of 2."
            processes = []
            self.status = Queue()
            for mdl in MaterializedView.__subclasses__():
                n = mdl.__name__
                control = get_control(mdl)
                if not control.enabled:
                    continue
                if limit_to_models:
                    if n not in limit_to_models:
                        continue
                else:
                    if not control.include_in_batch:
                        # This view must be evaluated separately.
                        continue
                #print mdl.__name__
                for i, _ in enumerate(xrange(multi)):
                    stripe = kwargs['stripe'] = '%i%i' % (i, multi)
                    kwargs['status'] = self.status
                    
                    connection.close()
                    p = Process(target=self.update, args=(mdl,), kwargs=kwargs)
                    p.daemon = True
                    processes.append(p)
                    p.start()
                self.progress[(mdl, stripe)] = (0, 0, 0, 0, None, '')
            #return
            while any(i.is_alive() for i in processes):
                time.sleep(0.1)
                while not self.status.empty():
                    (mdl, stripe), current, total, sub_current, sub_total, eta, message = self.status.get()
                    self.progress[(mdl, stripe)] = (current, total, sub_current, sub_total, eta, message)
                    self.start_times[(mdl, stripe)] = time.time()
                    self.print_progress()
            print 'All processes complete.'
        else:
            for mdl in MaterializedView.__subclasses__():
                n = mdl.__name__
                control = get_control(mdl)
                if not control.enabled:
                    continue
                if limit_to_models:
                    if n not in limit_to_models:
                        continue
                else:
                    if not control.include_in_batch:
                        # This view must be evaluated separately.
                        continue
                kwargs['status'] = self.status
                self.update(mdl, **kwargs)

    def print_progress(self, clear=True, newline=True):
        if self.last_progress_refresh and (datetime.now()-self.last_progress_refresh).seconds < 0.5:
            return
        bar_length = 10
        if clear:
            sys.stdout.write('\033[2J\033[H') #clear screen
            sys.stdout.write('Materializing views\n')
        for (mdl, stripe), (current, total, sub_current, sub_total, eta, message) in sorted(self.progress.items()):
            sub_status = ''
            
            if total:
                
                if not eta:
                    start_time = self.start_times[(mdl, stripe)]
                    current_seconds = time.time() - start_time
                    total_seconds = float(total)/current*current_seconds
                    remaining_seconds = int(total_seconds - current_seconds)
                    eta = timezone.now() + timedelta(seconds=remaining_seconds)
                    
                self.stripe_counts[(mdl, stripe)] = (current, total)
                percent = current/float(total)
                bar = ('=' * int(percent * bar_length)).ljust(bar_length)
                percent = int(percent * 100)
            else:
                eta = eta or '?'
                percent = 0
                bar = ('=' * int(percent * bar_length)).ljust(bar_length)
                percent = '?'
                total = '?'
            if sub_current and sub_total:
                sub_status = '(subtask %s of %s) ' % (sub_current, sub_total)
            sys.stdout.write(
                (('' if newline else '\r')+"%s [%s] %s of %s %s%s%% eta=%s: %s"+('\n' if newline else '')) \
                    % ('%s:%s' % (mdl.__name__, stripe), bar, current, total, sub_status, percent, eta, message))
        sys.stdout.flush()
        self.last_progress_refresh = datetime.now()
        
        # Update job.
        overall_current_count = 0
        overall_total_count = 0
        for (mdl, stripe), (current, total) in self.stripe_counts.iteritems():
            overall_current_count += current
            overall_total_count += total
        if overall_total_count and Job:
            Job.update_progress(
                total_parts_complete=overall_current_count,
                total_parts=overall_total_count,
            )

    def update(self, mdl, status=None, **kwargs):
        """
        Iterate over all materilized view models and materializes them.
        """
        
        stripe = kwargs.get('stripe')
        reraise = kwargs.get('reraise')
        
        current_count = 0
        total_count = 0
        fatal_errors = False
        fatal_error = None
        estimated_completion_datetime = None
        sub_current = 0
        sub_total = 0
        
        def print_status(message, count=None, total=None):
            #print 'message:',message
            current_count = count or 0
            total_count = total or 0
            if status:
                status.put([
                    (mdl, stripe),
                    current_count+1,
                    total_count,
                    sub_current,
                    sub_total,
                    estimated_completion_datetime,
                    message,
                ])
            else:
                self.progress[(mdl, stripe)] = (
                    current_count,
                    total_count,
                    sub_current,
                    sub_total,
                    estimated_completion_datetime,
                    message,
                )
                self.print_progress(clear=False, newline=False)
        
        try:
            print_status('Updating materialized view %s...' % str(mdl))
            mdl.materialize(print_status=print_status, **kwargs)
            print_status('Done.')
        except Exception, e:
            if reraise:
                raise
            print>>sys.stderr, 'Error while materializing view %s:' % str(mdl)
            traceback.print_exc(file=sys.stderr)
        