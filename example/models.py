# -*- coding: utf-8 -*-

from django.db import models
from sortedone2many.fields import SortedOneToManyField, inject_extra_field_to_model


class Item(models.Model):
    name = models.CharField(max_length=50)

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

# from django.contrib.auth.models import User
# inject_extra_field_to_model('auth.User', 'items', SortedOneToManyField(Item, sorted=True, blank=True))
# !! not working using string model_name
# 
class FixedCategory(models.Model):
    name = models.CharField(max_length=50)
# 
inject_extra_field_to_model(FixedCategory, 'items', SortedOneToManyField(Item, sorted=True, blank=True))


