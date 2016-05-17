# -*- coding: utf-8 -*-
import django
from django.db import models, router, transaction
from django.db.models.fields.related import (ManyToManyField, ManyToManyRel,
    RECURSIVE_RELATIONSHIP_CONSTANT)
if django.VERSION >= (1, 9):
    from django.db.models.fields.related import ManyToManyDescriptor as ManyRelatedObjectsDescriptor
else:
    from django.db.models.fields.related import ManyRelatedObjectsDescriptor
    
from django.utils import six
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _

from sortedm2m.fields import SortedManyToManyField, SORT_VALUE_FIELD_NAME
from sortedm2m.compat import get_foreignkey_field_kwargs

from .forms import SortedMultipleChoiceWithDisabledField


class OneToManyRel(ManyToManyRel):
    'the relationship (meta info) for a ``SortedOneToManyField``'
    def __init__(self, *args, **kwargs):
        super(OneToManyRel, self).__init__(*args, **kwargs)
        # set `multiple = False` as the `SortedOneToManyField` is on the
        # "one" side/forward side of the OneToMany Relation.
        # This affects the `get_accessor_name()` function, i.e. it will use
        # the lower-cased model name (without appending "_set" to it) as the
        # default related_name.
        self.multiple = False


class OneToManyRelatedObjectDescriptor(ManyRelatedObjectsDescriptor):
    '''
    Accessor to the related object (not the manager) on the reverse side of a 
    one-to-many relation.

    In the example::

        class Category(models.Model):
            items = SortedOneToManyField(Item, sorted=True)

    ``item.category`` is a OneToManyRelatedObjectDescriptor instance.

    It behaves similar to a ``SingleRelatedObjectDescriptor`` as it directly
    exposes the related object, but underneath it uses the ``manager`` of
    the many-to-many intermediary model (similar to the
    ``ManyRelatedObjectsDescriptor``).
    '''
    def __init__(self, related):
        self.related = self.rel = related
        self.cache_name = related.get_cache_name()
        self.sup = super(OneToManyRelatedObjectDescriptor, self)
        if django.VERSION >= (1, 9):
            self.reverse = True # always True

    def is_cached(self, instance):
        return hasattr(instance, self.cache_name)

    def get_manager(self, instance):
        # get the manager using ManyRelatedObjectsDescriptor
        return self.sup.__get__(instance)

    def get_prefetch_queryset(self, instances, queryset=None):
        instance = instances[0]
        manager = self.get_manager(instance)
        (queryset, rel_obj_attr, instance_attr, single, cache_name) = manager.get_prefetch_queryset(instances, queryset)
        single = True
        cache_name = self.cache_name
        return (queryset, rel_obj_attr, instance_attr, single, cache_name)

    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self
        try:
            rel_obj = getattr(instance, self.cache_name)
        except AttributeError:
            manager = self.get_manager(instance)
#             manager = ManyRelatedObjectsDescriptor.__get__(self, instance, instance_type)
            rel_obj_all = manager.all()
            count = rel_obj_all.count()
            if count == 0:
                return None
            elif count > 1:
                raise Exception('Multiple (%s) instances found for OneToMany field' % count)
            rel_obj = rel_obj_all[0]
            setattr(instance, self.cache_name, rel_obj)

        if rel_obj is None:
            raise self.RelatedObjectDoesNotExist(
                "%s has no %s." % (
                    instance.__class__.__name__,
                    self.related.get_accessor_name()
                )
            )
        else:
            return rel_obj

    def __set__(self, instance, value):
        if not self.related.field.rel.through._meta.auto_created:
            opts = self.related.field.rel.through._meta
            raise AttributeError(
                "Cannot set values on a ManyToManyField which specifies an "
                "intermediary model. Use %s.%s's Manager instead." % (opts.app_label, opts.object_name)
            )

        # if value is None, will simply remove this instance from the associated
        # related object

        # If null=True, we can assign null here, but otherwise the value needs
        # to be an instance of the related class.
#         if value is None and self.related.field.null is False:
#             raise ValueError(
#                 'Cannot assign None: "%s.%s" does not allow null values.' % (
#                     instance._meta.object_name,
#                     self.related.get_accessor_name(),
#                 )
#             )

        manager = self.get_manager(instance)
        set_cache = True
        if not isinstance(value, self.related.related_model):
            set_cache = False
            if isinstance(value, models.Model):
                raise ValueError(
                    'Cannot assign "%r": "%s.%s" must be a "%s" instance.' % (
                        value,
                        instance._meta.object_name,
                        self.related.get_accessor_name(),
                        self.related.related_model._meta.object_name,
                    )
                )
            elif value is None:
                set_cache = True
#                 try:
#                     print(manager.all(), value)
#                     value = manager.get(pk=value)
#                 except Exception:# self.related.related_model.DoesNotExist:
#                     raise ValueError(
#                         'Cannot assign "%r": it is not a valid pk of a "%s" instance.' % (
#                             value,
#                             self.related.related_model._meta.object_name,
#                         )
#                     )

        db = router.db_for_write(manager.through, instance=manager.instance)
        with transaction.atomic(using=db, savepoint=False):
            manager.clear()
            if value is not None:
                manager.add(value)

        if set_cache:
            # Since we already know what the related object is, seed the related
            # object caches now, too. This avoids another db hit if you get the
            # object you just set.
            setattr(instance, self.cache_name, value)
        else:
            # simply delete the cache, and it will be cached next time accessing it
            if hasattr(instance, self.cache_name):
                delattr(instance, self.cache_name)


class SortedOneToManyField(SortedManyToManyField):
    '''
    Provide a one-to-many relation that also remembers the order of related
    objects.

    Accept a boolean ``sorted`` attribute which specifies if relation is
    ordered or not. Default is set to ``True``.

    Based on ``SortedManyToManyField`` from the django-sortedm2m library
    (https://github.com/gregmuellegger/django-sortedm2m).

    It uses an intermediary model that holds a ForeignKey field pointed at
    the model on the forward side of the relation, a OneToOneField field
    pointed at the model on the remote side (to ensure each remote object
    only relates to a unique forward object), and another field storing the
    sort value (to remember to orders of the remote objects).

    In the example::
    
        class Category(models.Model):
            items = SortedOneToManyField(Item, sorted=True)

    ``category.items`` is the manager for related ``Item`` objects (the same as
    the normal ``ManyToManyField``, e.g. use it like ``category.items.add(new_item)``),
    while ``item.category`` is an instance (not manager) of ``Category`` (similar
    to a ``OneToOneField``, e.g., use it like ``item.category.pk``).
    '''
    # Field flags
    many_to_many = True  # keep this to use the same deeper hooks
    many_to_one = False
    one_to_many = True  # TODO: any side effects of these flags??
    one_to_one = False

    description = _("One-to-many relationship")

    def __init__(self, to, sorted=True, **kwargs):  # through_app_label=None,
        self.sorted = sorted
        self.sort_value_field_name = kwargs.pop(
            'sort_value_field_name',
            SORT_VALUE_FIELD_NAME)

        # not symmetrical as it is "one-to-many", even for RECURSIVE_RELATIONSHIP_CONSTANT
        kwargs['symmetrical'] = False

        # ManyToManyField.__init__():
        db_constraint = kwargs.pop('db_constraint', True)
        swappable = kwargs.pop('swappable', True)

        try:
            to._meta
        except AttributeError:  # to._meta doesn't exist, so it must be RECURSIVE_RELATIONSHIP_CONSTANT
            assert isinstance(to, six.string_types), (
                "%s(%r) is invalid. First parameter to SortedOneToManyField must be "
                "either a model, a model name, or the string %r" %
                (self.__class__.__name__, to, RECURSIVE_RELATIONSHIP_CONSTANT)
            )
            # Class names must be ASCII in Python 2.x, so we forcibly coerce it
            # here to break early if there's a problem.
            to = str(to)
        kwargs['verbose_name'] = kwargs.get('verbose_name', None)
        # !! changed from ManyToManyRel to OneToManyRel
        kwargs['rel'] = OneToManyRel(
            self, to,
            related_name=kwargs.pop('related_name', None),
            related_query_name=kwargs.pop('related_query_name', None),
            limit_choices_to=kwargs.pop('limit_choices_to', None),
            symmetrical=kwargs.pop('symmetrical', to == RECURSIVE_RELATIONSHIP_CONSTANT),
            through=kwargs.pop('through', None),
            through_fields=kwargs.pop('through_fields', None),
            db_constraint=db_constraint,
        )

        self.swappable = swappable
        self.db_table = kwargs.pop('db_table', None)
        if kwargs['rel'].through is not None:
            assert self.db_table is None, "Cannot specify a db_table if an intermediary model is used."

        super(ManyToManyField, self).__init__(**kwargs)
        if django.VERSION >= (1, 9):
            self.has_null_arg = 'null' in kwargs

        if self.sorted:
            self.help_text = kwargs.get('help_text', None)

    def formfield(self, **kwargs):
        defaults = {}
        if self.sorted:
            defaults['form_class'] = SortedMultipleChoiceWithDisabledField
        # related_query_name is required for the SortedMultipleChoiceWithDisabledField
        # to decide which items are not null (together with queryset)
        defaults['related_query_name'] = self.related_query_name()
        defaults.update(kwargs)
        return super(SortedManyToManyField, self).formfield(**defaults)

    def get_intermediate_model_to_field(self, klass):
        name = self.get_intermediate_model_name(klass)

        to_model, to_object_name = self.get_rel_to_model_and_object_name(klass)

        if self.rel.to == RECURSIVE_RELATIONSHIP_CONSTANT or to_object_name == klass._meta.object_name:
            field_name = 'to_%s' % to_object_name.lower()
        else:
            field_name = to_object_name.lower()

        # !! changed from ForeignKey to OneToOneField
        field = models.OneToOneField(to_model, related_name='%s+' % name,
                                     **get_foreignkey_field_kwargs(self))

        return field_name, field

    def contribute_to_related_class(self, cls, related):
        # Internal M2Ms (i.e., those with a related name ending with '+')
        # and swapped models don't get a related descriptor.
        # !! changed to `OneToManyRelatedObjectDescriptor`
        if not self.rel.is_hidden() and not related.related_model._meta.swapped:
            setattr(cls, related.get_accessor_name(), OneToManyRelatedObjectDescriptor(related))

        # Set up the accessors for the column names on the m2m table
        self.m2m_column_name = curry(self._get_m2m_attr, related, 'column')
        self.m2m_reverse_name = curry(self._get_m2m_reverse_attr, related, 'column')

        self.m2m_field_name = curry(self._get_m2m_attr, related, 'name')
        self.m2m_reverse_field_name = curry(self._get_m2m_reverse_attr, related, 'name')

        get_m2m_rel = curry(self._get_m2m_attr, related, 'rel')
        self.m2m_target_field_name = lambda: get_m2m_rel().field_name
        get_m2m_reverse_rel = curry(self._get_m2m_reverse_attr, related, 'rel')
        self.m2m_reverse_target_field_name = lambda: get_m2m_reverse_rel().field_name



