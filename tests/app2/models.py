# -*- coding: utf-8 -*-

from django.db import models
from sortedone2many.fields import SortedOneToManyField
from sortedone2many.utils import inject_extra_field_to_model


class M1(models.Model):
    name = models.CharField(max_length=50)


class M2(models.Model):
    name = models.CharField(max_length=50)
