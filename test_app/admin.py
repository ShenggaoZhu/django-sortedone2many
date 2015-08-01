# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models.fields.related import ManyToOneRel

from django import forms
from django.utils import six
from test_app.models import Item, Category, CategorySelf, FixedCategory
from sortedone2many.fields import OneToManyRel, SortedOneToManyField
# from guardian.admin import GuardedModelAdmin
# from userena.admin import *

from django.forms.models import ModelFormMetaclass


class One2ManyModelFormMetaclass(ModelFormMetaclass):
    # find One2Many fields from the model and auto add them to the form

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

                related_fields = model._meta.get_all_related_many_to_many_objects()
                for field in related_fields:
                    if not isinstance(field, OneToManyRel):
                        continue
                    related_one2manyfields.append(field)
                    related_model = field.related_model
                    related_name = field.name
                    attrs[related_name] = forms.ModelChoiceField(queryset=related_model.objects.all())
#         attrs['one2manyfields'] = one2manyfields
        attrs['related_one2manyfields'] = related_one2manyfields
        new_class = super(One2ManyModelFormMetaclass, mcs).__new__(mcs, name, bases, attrs)
        return new_class


class One2ManyModelForm(six.with_metaclass(One2ManyModelFormMetaclass, forms.ModelForm)):

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
        related_fields = self.opts.get_all_related_many_to_many_objects()
        for field in related_fields:
            if not isinstance(field, OneToManyRel):
                continue
            self.related_one2manyfields.append(field.name)

    def save_model(self, request, obj, form, change):
        super(One2ManyModelAdmin, self).save_model(request, obj, form, change)
        for name in self.related_one2manyfields:
            try:
                setattr(obj, name, form.cleaned_data[name])
            except Exception as e:
                print(e)


class ItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        try:
            self.fields['category'].initial = self.instance.category
        except ValueError:
            pass
        rel = ManyToOneRel(self.instance._meta.get_field('category'),
                           Category,
                           Category._meta.pk.name)
#         rel = self.instance._meta.get_field('category')
        self.fields['category'].widget = RelatedFieldWidgetWrapper(self.fields['category'].widget, rel, self.admin_site, can_change_related=True)

    category = forms.ModelChoiceField(queryset=Category.objects.all())

    class Meta:
        model = Item
        exclude = []

class ItemAdmin(admin.ModelAdmin):
    model = Item
    form = ItemForm

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        print('admin_site', admin_site)
        raise
        super(ItemAdmin, self).__init__(model, admin_site)

    def save_model(self, request, obj, form, change):
        super(ItemAdmin, self).save_model(request, obj, form, change)
        obj.category = form.cleaned_data['category']


admin.site.register(Item, One2ManyModelAdmin)
admin.site.register(Category, One2ManyModelAdmin)
admin.site.register(CategorySelf, One2ManyModelAdmin)
admin.site.register(FixedCategory)

