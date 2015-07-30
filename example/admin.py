# -*- coding: utf-8 -*-
from django.contrib import admin
from example.models import Item, Category, CategorySelf

admin.site.register(Item)
admin.site.register(Category)
admin.site.register(CategorySelf)
