
class MaterializedView(object):
    """
    An interface for managing periodically updated materialized views.
    """
    
    @classmethod
    def materialize(cls, do_insert=True, do_update=True, do_delete=True, **kwargs):
        if do_insert:
            cls.do_insert(**kwargs)
        if do_update:
            cls.do_update(**kwargs)
        if do_delete:
            cls.do_delete(**kwargs)

    @classmethod
    def do_insert(cls, *args, **kwargs):
        return

    @classmethod
    def do_update(cls, *args, **kwargs):
        return

    @classmethod
    def do_delete(cls, *args, **kwargs):
        return
    
    @classmethod
    def needs_insert(cls, *args, **kwargs):
        return False

    @classmethod
    def needs_update(cls, *args, **kwargs):
        return False
        
    @classmethod
    def needs_delete(cls, *args, **kwargs):
        return False

    @classmethod
    def is_fresh(cls):
        needs_insert = cls.needs_insert()
        if needs_insert:
            return False
        needs_update = cls.needs_update()
        if needs_update:
            return False
        needs_delete = cls.needs_delete()
        if needs_delete:
            return False
        return True
    