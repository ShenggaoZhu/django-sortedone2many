# -*- coding: utf-8 -*-

from django.db import models
from sortedone2many.fields import SortedOneToManyField
from sortedone2many.utils import inject_extra_field_to_model


class Item(models.Model):
    name = models.CharField(max_length=50)
    fk = models.ForeignKey('Category', blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50)
    items = SortedOneToManyField(Item, sorted=True, blank=True)

    def __str__(self):
        return self.name


class CategorySelf(models.Model):
    name = models.CharField(max_length=50)
    items = SortedOneToManyField('self', sorted=True, related_name='category', blank=True)

    def __str__(self):
        return self.name


class FixedCategory(models.Model):
    name = models.CharField(max_length=50)

inject_extra_field_to_model(FixedCategory, 'items', SortedOneToManyField(Item, sorted=True, blank=True))

from django.contrib.auth.models import User
inject_extra_field_to_model(User, 'items', SortedOneToManyField(Item, related_name='owner'))



