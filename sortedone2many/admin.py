# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models.fields.related import ManyToOneRel, ManyToManyField
from django import forms
from django.utils import six

from .fields import OneToManyRel

from django.forms.models import ModelFormMetaclass

import django
if django.VERSION >= (1, 9):
    def get_all_related_many_to_many_objects(_meta):
        return [obj for obj in _meta.get_fields() if isinstance(obj, ManyToManyField)]
else:
    def get_all_related_many_to_many_objects(_meta):
        return _meta.get_all_related_many_to_many_objects()


class One2ManyModelFormMetaclass(ModelFormMetaclass):
    '''
    Metaclass to find related One2Many fields from the model defined in the
    Form's Meta class, and automatically add these related One2Many fields to
    the Form as ``ModelChoiceField`` fields.
    '''

    def __new__(mcs, name, bases, attrs):
        Meta = attrs.get('Meta', None)
#         one2manyfields = []
        related_one2manyfields = []
        if Meta:
            model = getattr(Meta, 'model', None)
            if model:
#                 for field in model._meta.get_fields():
#                     if isinstance(field, SortedOneToManyField):
#                         one2manyfields.append(field)

                related_fields = get_all_related_many_to_many_objects(model._meta)
                for field in related_fields:
                    if not isinstance(field, OneToManyRel):
                        continue
                    related_one2manyfields.append(field)
                    related_model = field.related_model
                    related_name = field.name
                    attrs[related_name] = forms.ModelChoiceField(
                        queryset=related_model.objects.all(),
                        required=False)
#         attrs['one2manyfields'] = one2manyfields
        attrs['related_one2manyfields'] = related_one2manyfields
        new_class = super(One2ManyModelFormMetaclass, mcs).__new__(mcs, name, bases, attrs)
        return new_class


class One2ManyModelForm(six.with_metaclass(One2ManyModelFormMetaclass, forms.ModelForm)):
    '''
    Find related One2Many fields from the model defined in the
    Form's Meta class, and automatically add these related One2Many fields to
    the Form as ``ModelChoiceField`` fields.

    Wrap the ``ModelChoiceField`` (for related One2Many fields of the model) 
    with ``RelatedFieldWidgetWrapper`` using a fake ``ManyToOneRel``, so that
    the ``ModelChoiceField`` will be rendered in the Admin site as a dropdown 
    <select> list with additional "change" and "add" buttons (two small green 
    buttons just like in the widget of a ``ForeinKey`` field).
    '''
    def __init__(self, *args, **kwargs):
        super(One2ManyModelForm, self).__init__(*args, **kwargs)
        admin_site = getattr(self, 'admin_site', admin.site)

        for field in self.related_one2manyfields:
            related_model = field.related_model
            related_name = field.name
            fake_manytoone_rel = ManyToOneRel(field,
                                              related_model,
                                              related_model._meta.pk.name)

            try:
                self.fields[related_name].initial = getattr(self.instance, related_name, None)
            except Exception:
                pass

            self.fields[related_name].widget = RelatedFieldWidgetWrapper(
                self.fields[related_name].widget, fake_manytoone_rel,
                admin_site, can_change_related=True)


class One2ManyModelAdmin(admin.ModelAdmin):
    '''
    A customized ModelAdmin class that displays and saves the related One2Many
    fields of the model instance. Works hand in hand with ``One2ManyModelForm``.
    '''
    form = One2ManyModelForm

    def __init__(self, model_cls, admin_site):

        class FormWithModel(One2ManyModelForm):
            class Meta:
                model = model_cls
                exclude = []
        self.form = FormWithModel

        super(One2ManyModelAdmin, self).__init__(model_cls, admin_site)
        self.form.admin_site = admin_site  # used in the form

        self.related_one2manyfields = []
        related_fields = get_all_related_many_to_many_objects(self.opts)
        for field in related_fields:
            if not isinstance(field, OneToManyRel):
                continue
            self.related_one2manyfields.append(field.name)

    def save_model(self, request, obj, form, change):
        super(One2ManyModelAdmin, self).save_model(request, obj, form, change)
        # save related_one2manyfields
        for name in self.related_one2manyfields:
            try:
                setattr(obj, name, form.cleaned_data[name])
            except Exception as e:
                pass

def register(model_or_iterable, admin_class=One2ManyModelAdmin, **options):
    '''
    A shortcut function to register ``model_or_iterable`` using
    ``One2ManyModelAdmin`` as the default admin class.
    '''
    admin.site.register(model_or_iterable, admin_class, **options)







