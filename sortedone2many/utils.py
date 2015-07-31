# -*- coding: utf-8 -*-

from django.utils import six
from sortedone2many.fields import SortedOneToManyField


def inject_extra_field_to_model(from_model, field_name, field):
    if not isinstance(from_model, six.string_types):
        field.contribute_to_class(from_model, field_name)
        return
    raise Exception('from_model must be a Model Class')

#     app_label, model_name = from_model.split('.')
#     from django.apps import apps
#     try:
#         from_model_cls = apps.get_registered_model(app_label, model_name)
#         field.contribute_to_class(from_model_cls, field_name)
#     except:
#         from django.db.models.signals import class_prepared
#         def add_field(sender, **kwargs):
#             if sender.__name__ == model_name and sender._meta.app_label == app_label:
#                 field.contribute_to_class(sender, field_name)
#         # TODO: `add_field` is never called. `class_prepared` already fired or never fire??
#         class_prepared.connect(add_field)


def add_sorted_one2many_relation(model_one,
                                 model_many,
                                 field_name_on_model_one=None,
                                 related_name_on_model_many=None):
    field_name = field_name_on_model_one or model_many._meta.model_name + '_set'
    related_name = related_name_on_model_many or model_one._meta.model_name
    field = SortedOneToManyField(model_many, related_name=related_name)
    field.contribute_to_class(model_one, field_name)

