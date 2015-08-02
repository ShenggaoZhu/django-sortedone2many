# -*- coding: utf-8 -*-
# from django.contrib import admin

from test_app.models import Item, Category, CategorySelf, FixedCategory
from sortedone2many.admin import register

# admin.site.register(Item)
register(Item)
register(Category)
register(CategorySelf)
register(FixedCategory)

