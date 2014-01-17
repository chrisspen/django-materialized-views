
class MaterializedView(object):
    """
    An interface for managing periodically updated materialized views.
    """
    
    stripable = False
    
    def print_status(self, message):
        print message
    
    @classmethod
    def materialize(cls, do_insert=True, do_update=True, do_delete=True, stripe=None, print_status=None, **kwargs):
        if not self.stripable and stripe is not None:
            return
        print_status = print_status or self.print_status
        if do_insert:
            cls.do_insert(stripe=stripe, print_status=print_status, **kwargs)
        if do_update:
            cls.do_update(stripe=stripe, print_status=print_status, **kwargs)
        if do_delete:
            cls.do_delete(stripe=stripe, print_status=print_status, **kwargs)

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
    