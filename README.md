=======================================================================
django-materialized-views - A simple Django materialized view framework
=======================================================================

Overview
========

This implements a simple interface and management command for updating
and maintaining cached or calculated tables in small batches.

Usage
-----

To use, subclass the parent class and override the 6 methods for
detecting and performing insert, update and deletions, e.g.

    from django_materialized_views.models import MaterializedView
    
    class MyModel(models.Model, MaterializedView):
    
        key = models.CharField(max_length=100, db_index=True, unique=True)
        
        cached_value = models.CharField(max_length=100, db_index=True)
        
        @classmethod
        def needs_insert(cls):
            # This returns true if there are new materialized records we need to create.
            return MyOtherTable.objects.exclude(value__in=cls.objects.all().values_list('cached_value').count()
    
        @classmethod
        def needs_update(cls):
            # This returns true if there are new materialized records we need to update.
            return MyOtherTable.objects.filter(some_criteria_date__gt=date.today()-timedelta(days=7)).count()
            
        @classmethod
        def needs_delete(cls):
            # This returns true if there are new materialized records we need to delete.
            return MyOtherTable.objects.filter(deleted__isnull=False).count()
        
        @classmethod
        def do_insert(cls):
            for r in MyOtherTable.objects.get_new():
                cls.objects.create(key=r.key, cached_value=r.value)
    
        @classmethod
        def do_update(cls):
            for r in MyOtherTable.objects.get_updated():
                obj, _ = cls.objects.get_or_create(key=r.key, cached_value=r.value)
                obj.cached_value = r.value
                obj.save()
    
        @classmethod
        def do_delete(cls):
            cls.objects.filter(key__in=MyOtherTable.objects.get_obsolete().values_list('key')).delete()

Then schedule the management command `update_materialized_views`, via cron
or similar scheduler, to run as often as you'd like the materialized view to be
updated.

By default, this will update all subclasses of `MaterializedView`, but you can
specify a specific subclass using the `--models` parameter.
