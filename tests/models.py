# -*- coding: utf-8 -*-

from django.db import models
from sortedone2many.fields import SortedOneToManyField
from sortedone2many.utils import inject_extra_field_to_model


class Item(models.Model):
    name = models.CharField(max_length=50)


class Category(models.Model):
    name = models.CharField(max_length=50)
    items = SortedOneToManyField(Item, sorted=True, blank=True)

# from django.apps import apps
# print('apps.ready', apps.ready)


class CategorySelf(models.Model):
    name = models.CharField(max_length=50)
    items = SortedOneToManyField('self', sorted=True, related_name='category', blank=True)


class ItemStringRef(models.Model):
    name = models.CharField(max_length=50)


class CategoryStringRef(models.Model):
    name = models.CharField(max_length=50)
    items = SortedOneToManyField('ItemStringRef', sorted=True, related_name='category', blank=True)


class ItemFixed(models.Model):
    name = models.CharField(max_length=50)


class CategoryFixed(models.Model):
    name = models.CharField(max_length=50)

inject_extra_field_to_model(CategoryFixed, 'items',
    SortedOneToManyField(ItemFixed, sorted=True, related_name='category', blank=True))


from .app2.models import M1, M2

inject_extra_field_to_model(M1, 'items',
    SortedOneToManyField(M2, sorted=True, related_name='category', blank=True))



