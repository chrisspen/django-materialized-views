from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

try:
    from admin_steroids.utils import StringWithTitle
    APP_LABEL = StringWithTitle('django_materialized_views', 'Materialized Views')
except ImportError:
    APP_LABEL = 'django_materialized_views'
    
def parse_stripe(stripe):
    stripe_num = None
    stripe_mod = None
    if stripe:
        assert isinstance(stripe, basestring) and len(stripe) == 2
        stripe_num,stripe_mod = stripe
        stripe_num = int(stripe_num)
        stripe_mod = int(stripe_mod)
        assert stripe_num < stripe_mod
    return stripe_num, stripe_mod

class MaterializedViewControl(models.Model):
    
    name = models.CharField(
        max_length=500,
        blank=False,
        null=False,
        editable=False)
    
    app_label = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        editable=False)
    
    enabled = models.BooleanField(
        default=True,
        help_text=_('If checked, this model will be routinely updated.'))
    
    stripable = models.BooleanField(
        default=False,
        help_text=_('''If checked, implies insert/update/delete methods accept
            a valid stripe parameter that tell them to segment query during
            multiprocessing.'''))
    
    include_in_batch = models.BooleanField(
        default=True,
        help_text=_('''If checked, will be materialized when the
            update_materialized_views command is run with no model name
            specified. This is useful when a specific model is especially
            long-running or should be rarely or conditionally run or otherwise
            not run with the other views.'''))
    
    class Meta:
        app_label = APP_LABEL
        verbose_name = _('control')
        verbose_name_plural = _('controls')
        unique_together = (
            ('name', 'app_label'),
        )

class MaterializedView(object):
    """
    An interface for managing periodically updated materialized views.
    """
    
    matview_stripable = False
    
    matview_include_in_batch = True
    
    def print_status(cls, message):
        print message
    
    @classmethod
    def matview_materialize(cls,
        do_insert=True,
        do_update=True,
        do_delete=True,
        stripe=None,
        print_status=None,
        **kwargs):
        
        if not cls.matview_stripable and stripe is not None and stripe[0] != '0':
            # If this view isn't stripable, then only process the first stripe.
            return
        
        print_status = print_status or cls.print_status
        if do_insert:
            cls.matview_insert(stripe=stripe, print_status=print_status, **kwargs)
        if do_update:
            cls.matview_update(stripe=stripe, print_status=print_status, **kwargs)
        if do_delete:
            cls.matview_delete(stripe=stripe, print_status=print_status, **kwargs)

    @classmethod
    def matview_insert(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def matview_update(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def matview_delete(cls, *args, **kwargs):
        raise NotImplementedError
    
    @classmethod
    def matview_needs_insert(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def matview_needs_update(cls, *args, **kwargs):
        raise NotImplementedError
        
    @classmethod
    def matview_needs_delete(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def matview_is_fresh(cls):
        needs_insert = cls.matview_needs_insert()
        if needs_insert:
            return False
        needs_update = cls.matview_needs_update()
        if needs_update:
            return False
        needs_delete = cls.matview_needs_delete()
        if needs_delete:
            return False
        return True
    