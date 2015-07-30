# -*- coding: utf-8 -*-

from django.db import models

from django.db import connection
from django.db.models.fields import FieldDoesNotExist
from django.test.utils import override_settings
from django.utils import six

from django.test import TestCase
from django.db.utils import IntegrityError
from .models import *

str_ = six.text_type

# Note:
# one test function can only have one self.assertRaisesMessage(...),
# otherwise the following error occurs:
#     django.db.transaction.TransactionManagementError: An error occurred in the
#     current transaction. You can't execute queries until the end of the 'atomic' block.


class TestSortedOneToManyField(TestCase):
    # modified from ``SortedManyToManyField`` tests
    M_Cat = Category
    M_Item = Item

    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.cats = [cls.M_Cat.objects.create(name="cat%s" % i) for i in range(2)]
        cls.items = [cls.M_Item.objects.create(name="item%s" % i) for i in range(10)]

    def assertRaisesUniqueFailed(self, callable_obj=None, *args, **kwargs):
        self.assertRaisesMessage(IntegrityError, 'UNIQUE constraint failed:',
                                callable_obj, *args, **kwargs)

    def test_add_items(self):

        cat = self.cats[0]
        self.assertEqual(list(cat.items.all()), [])

        cat.items.add(self.items[2])
        self.assertEqual(list(cat.items.all()), [self.items[2]])

        # adding many with each in one call
        cat.items.add(self.items[5])
        cat.items.add(self.items[1])
        self.assertEqual(list(cat.items.all()), [
            self.items[2],
            self.items[5],
            self.items[1]])

        # adding the same item again won't append another one, order remains
        # the same
        cat.items.add(self.items[2])
        self.assertEqual(list(cat.items.all()), [
            self.items[2],
            self.items[5],
            self.items[1]])

        cat.items.clear()
        self.assertEqual(list(cat.items.all()), [])

        # adding many with all in the same call
        cat.items.add(self.items[3], self.items[1], self.items[2])
        self.assertEqual(list(cat.items.all()), [
            self.items[3],
            self.items[1],
            self.items[2]])

        cat.items.clear()
        self.assertEqual(list(cat.items.all()), [])

        # adding duplicate items in one call
        cat.items.add(self.items[3], self.items[3])
        self.assertEqual(list(cat.items.all()), [
            self.items[3]])

    def test_adding_items_by_pk(self):
        cat = self.cats[0]
        self.assertEqual(list(cat.items.all()), [])

        cat.items.add(self.items[2].pk)
        self.assertEqual(list(cat.items.all()), [self.items[2]])

        cat.items.add(self.items[5].pk, str_(self.items[1].pk))
        self.assertEqual(list(cat.items.all()), [
            self.items[2],
            self.items[5],
            self.items[1]])

        cat.items.clear()
        self.assertEqual(list(cat.items.all()), [])

        cat.items.add(self.items[3].pk, self.items[1], str_(self.items[2].pk))
        self.assertEqual(list(cat.items.all()), [
            self.items[3],
            self.items[1],
            self.items[2]])

    def test_add_items_unique_constraint(self):
        cat = self.cats[0]
        self.assertEqual(list(cat.items.all()), [])

        cat.items.add(self.items[1], self.items[2])
        self.assertEqual(list(cat.items.all()), [self.items[1], self.items[2]])

        cat2 = self.cats[1]
        self.assertEqual(list(cat2.items.all()), [])

#         cat2.items.add(self.items[2])
        self.assertRaisesUniqueFailed(cat2.items.add, self.items[2])

    def test_add_items_unique_constraint_by_pk(self):
        # add by pk
        cat = self.cats[0]
        self.assertEqual(list(cat.items.all()), [])

        cat.items.add(self.items[1], self.items[2])
        self.assertEqual(list(cat.items.all()), [self.items[1], self.items[2]])

        cat2 = self.cats[1]
        self.assertEqual(list(cat2.items.all()), [])
        self.assertRaisesUniqueFailed(cat2.items.add, self.items[2].pk)

    def test_reverse_related_object(self):
        cat = self.cats[0]
        self.assertEqual(list(cat.items.all()), [])

        cat.items.add(self.items[1], self.items[2])

        self.assertEqual(self.items[1].category, cat)
        self.assertEqual(self.items[2].category, cat)

        # None for not related object
        self.assertEqual(self.items[3].category, None)

        # directly assign category
        self.items[3].category = cat
        self.assertEqual(self.items[3].category, cat)

        cat2 = self.cats[1]
        self.assertEqual(list(cat2.items.all()), [])

        # directly change category
        self.items[3].category = cat2
        self.assertEqual(self.items[3].category, cat2)

        self.assertEqual(list(cat2.items.all()), [self.items[3]])

    def test_set_items(self):
        cat = self.cats[0]
        self.assertEqual(list(cat.items.all()), [])

        items = self.items[5:2:-1]
        cat.items = items
        self.assertEqual(list(cat.items.all()), items)

        items.reverse()
        cat.items = items
        self.assertEqual(list(cat.items.all()), items)

        cat.items.add(self.items[8])
        self.assertEqual(list(cat.items.all()), items + [self.items[8]])

        cat.items = []
        self.assertEqual(list(cat.items.all()), [])

        cat.items = [self.items[9]]
        self.assertEqual(list(cat.items.all()), [
            self.items[9]])

        cat.items = []
        self.assertEqual(list(cat.items.all()), [])

    def test_set_items_by_pk(self):
        cat = self.cats[0]
        self.assertEqual(list(cat.items.all()), [])

        books = self.items[5:2:-1]
        cat.items = [b.pk for b in books]
        self.assertEqual(list(cat.items.all()), books)

        cat.items = [self.items[5].pk, self.items[2]]
        self.assertEqual(list(cat.items.all()), [
            self.items[5],
            self.items[2]])

        cat.items = [str_(self.items[8].pk)]
        self.assertEqual(list(cat.items.all()), [self.items[8]])

    def test_remove_items(self):
        cat = self.cats[0]
        cat.items = self.items[2:5]
        self.assertEqual(list(cat.items.all()), [
            self.items[2],
            self.items[3],
            self.items[4]])

        cat.items.remove(self.items[3])
        self.assertEqual(list(cat.items.all()), [
            self.items[2],
            self.items[4]])

        cat.items.remove(self.items[2], self.items[4])
        self.assertEqual(list(cat.items.all()), [])

    def test_remove_items_by_pk(self):
        cat = self.cats[0]
        cat.items = self.items[2:5]
        self.assertEqual(list(cat.items.all()), [
            self.items[2],
            self.items[3],
            self.items[4]])

        cat.items.remove(self.items[3].pk)
        self.assertEqual(list(cat.items.all()), [
            self.items[2],
            self.items[4]])

        cat.items.remove(self.items[2], str_(self.items[4].pk))
        self.assertEqual(list(cat.items.all()), [])

#    def test_add_relation_by_hand(self):
#        cat = self.cats[0]
#        cat.items = self.items[2:5]
#        self.assertEqual(list(cat.items.all()), [
#            self.items[2],
#            self.items[3],
#            self.items[4]])
#
#        cat.items.create()
#        self.assertEqual(list(cat.items.all()), [
#            self.items[2],
#            self.items[3],
#            self.items[4]])

    # to enable population of connection.queries
    @override_settings(DEBUG=True)
    def test_prefetch_related_queries_num(self):
        cat = self.cats[0]
        cat.items.add(self.items[0])

        cat = self.M_Cat.objects.filter(pk=cat.pk).prefetch_related('items')[0]
        queries_num = len(connection.queries)
        name = cat.items.all()[0].name
        self.assertEqual(queries_num, len(connection.queries))

    def test_prefetch_related_sorting(self):
        cat = self.cats[0]
        items = [self.items[0], self.items[2], self.items[1]]
        cat.items = items

        cat = self.M_Cat.objects.filter(pk=cat.pk).prefetch_related('items')[0]

        def get_ids(queryset):
            return [obj.id for obj in queryset]
        self.assertEqual(get_ids(cat.items.all()), get_ids(items))

    def test_prefetch_reverse_related_object(self):
        cat = self.cats[0]
        cat.items.add(self.items[0])

        item = self.M_Item.objects.filter(pk=self.items[0].pk).prefetch_related('category')[0]
        queries_num = len(connection.queries)
        self.assertEqual(queries_num, len(connection.queries))

        # category object should be cached on item
        cache_name = item._meta.get_field('category').get_cache_name()  # '_category_cache'

        self.assertIn(cache_name, item.__dict__)
        self.assertEqual(item.__dict__[cache_name], cat)
        self.assertEqual(item.category, cat)


class TestSelfReference(TestSortedOneToManyField):
    M_Cat = CategorySelf
    M_Item = CategorySelf

    def test_add_self_to_items(self):
        cat = self.cats[0]
        cat.items.add(cat)
        self.assertEqual(list(cat.items.all()), [cat])

    def test_add_self_to_items_unique_constraint(self):
        cat = self.cats[0]
        cat.items.add(cat)
        cat2 = self.cats[1]
        self.assertRaisesUniqueFailed(cat2.items.add, cat)



class TestStringReference(TestSortedOneToManyField):
    M_Cat = CategoryStringRef
    M_Item = ItemStringRef


# not working

# from django.contrib.auth.models import User
# from django.db.models.signals import class_prepared
# class_prepared.send(User, **{'class':User})

class TestAddExtraField(TestSortedOneToManyField):
    M_Cat = CategoryFixed
#     M_Cat = User
    M_Item = ItemFixed


#     @classmethod
#     def setUpTestData(cls):
#         # Set up data for the whole TestCase
#         cls.cats = [cls.M_Cat.objects.create(username="cat%s" % i) for i in range(2)]
#         cls.items = [cls.M_Item.objects.create(name="item%s" % i) for i in range(10)]
#         
        