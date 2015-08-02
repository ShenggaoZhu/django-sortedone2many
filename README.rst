=====================
django-sortedone2many
=====================

``sortedone2many`` provides a ``SortedOneToManyField`` for django Model that establishes a 
one-to-many relationship (which can also remember the order of related objects).

Depends on ``SortedManyToManyField`` from the great library django-sortedm2m_ (check it out!).

.. _django-sortedm2m: https://github.com/gregmuellegger/django-sortedm2m


Usecases
========

Sorted ``OneToMany`` relationship
---------------------------------

The ``OneToMany`` relationship has been long missing from django ORM.
A similar relationship, ``ManyToOne``, is provided via a ``ForeignKey``,
which is always declared on the "many" side of the relationship.
In the following example (using ``related_name`` on a ``ForeignKey``)::

    class Category(models.Model):
        name = models.CharField(max_length=50)
        
    class Item(models.Model):
        category = ForeignKey(Category, related_name="items")

``item.category`` is a ``ManyToOne`` relationship, while 
``category.items`` is a ``OneToMany`` relationship. 
However, it is not easy to 
manage the order of the list of ``items`` in a ``category``.

To address this need, simply add a ``SortedOneToManyField`` (from this package) to 
the model on the "one" side of the relationship::

    class Category(models.Model):
        name = models.CharField(max_length=50)
        items = SortedOneToManyField(Item, sorted=True, blank=True)

``SortedOneToManyField`` uses an intermediary model with an extra
``sort_value`` field to manage the orders of the related objects.
It is very useful to represent **an ordered list of items** 
(according to their added order or manually arrangement).

Also, ``OneToMany`` relationship offers better **semantics** and **readability** than ``ForeignKey``,
especially for scenarios like ``master-detail`` or ``category-item`` 
(`this blog explains it nicely <http://blog.amir.rachum.com/blog/2013/06/15/a-case-for-a-onetomany-relationship-in-django/>`_).

Adding ``OneToMany`` to existing models
---------------------------------------

Since ``OneToMany`` relationship uses an intermediary model, 
it can work without altering already-existing models/tables,
thus providing better **extensibility** than ``ForeignKey``
(which requires adding a ``ForeignKey`` field to the model/table).
This is a big advantage when the existing models can't be changed
(e.g., models in a third-party library, or shared among several applications).

This package provides a shortcut function ``add_sorted_one2many_relation`` 
to inject ``OneToMany`` relationship to existing models without editing the 
model source code or subclassing the models.


Usage
=====

Add the ``SortedOneToManyField`` to the model on the "one" side of the 
relationship (as opposed to ``ForeignKey`` on the "many" side)::

    from django.db import models
    from sortedone2many.fields import SortedOneToManyField
    
    class Item(models.Model):
        name = models.CharField(max_length=50)
    
    class Category(models.Model):
        name = models.CharField(max_length=50)
        items = SortedOneToManyField(Item, sorted=True, blank=True)

Here, ``category.items`` is the manager for related ``Item`` objects (the same as
the normal ``ManyToManyField``, e.g. use it like ``category.items.add(new_item)``),
while ``item.category`` is an instance (not manager) of ``Category`` (similar
to a ``OneToOneField``, e.g., use it like ``item.category.pk``)..

Strictly speaking, ``item.category`` is an instance of 
``sortedone2many.fields.OneToManyRelatedObjectDescriptor``,
which directly exposes the (single) related object.
This is different from the ``ManyRelatedObjectsDescriptor`` (as in the normal ``ManyToManyField``)
which exposes the ``manager`` of the (multiple) related objects.

``SortedOneToManyField``
------------------------
Similar to ``SortedManyToManyField``, 
it uses an intermediary model that holds a ForeignKey field pointed at
the model on the "one" side of the relationship, a OneToOneField field
pointed at the model on the "many" side (to ensure the unique relationship 
to the "one" side), and another field storing the
sort value (to remember to orders of the objects on the "many" side).

``SortedOneToManyField`` accepts a boolean ``sorted`` attribute which specifies if relationship is
ordered or not. Default is set to ``True``.

Refer to django-sortedm2m_ for more details.

Admin
_____

First, add ``"sortedm2m"`` to your ``INSTALLED_APPS`` settings, 
which provides the static ``js`` and ``css`` files to render 
the related objects in a ``SortedOneToManyField`` as a list of 
checkboxes that can be sorted by drag'n'drop.
(That is the same as the behavior of a ``SortedManyToManyField``).

By default, a ``SortedOneToManyField`` is translated into a form field
``sortedone2many.forms.SortedMultipleChoiceWithDisabledField`` for rendering.
This form field also adds a special function to the widget:
disables those checkboxes that should not be directly selected 
on the current admin view (to ensure the unique ``OneToMany`` relationship).

E.g., in the image below, on the admin view for ``category 1``, 
``item1.category`` is ``category 2``, so the checkbox for ``item1`` is disabled
because ``category 2`` has to remove ``item1`` from its ``items`` list before
``category 1`` can select ``item1`` in the admin view.

.. image:: https://raw.githubusercontent.com/ShenggaoZhu/django-sortedone2many/master/docs/category.jpg

.. image:: https://raw.githubusercontent.com/ShenggaoZhu/django-sortedone2many/master/docs/item.jpg


Utility functions
-----------------
Use the following helper functions to inject extra fields to existing models:

+ ``inject_extra_field_to_model(from_model, field_name, field)``

+ ``add_sorted_one2many_relation(model_one, model_many, field_name_on_model_one=None, related_name_on_model_many=None)``

Working with existing models
----------------------------
``SortedOneToManyField`` can be added to an existing model that can't be edited directly
(e.g., in another library/app). For example, add to the ``User`` model in ``django.contrib.auth.models``.

It is recommended to use `django migrations`_ to do this.

.. _`django migrations`: https://docs.djangoproject.com/en/1.8/topics/migrations/

1. First, add the existing model (``User``) into django ``migrations`` using a migrations folder 
   **outside the original library/app** (e.g., in your own app). 
   This can be achieved by configuring the ``MIGRATION_MODULES`` dictionary in your django ``settings``::

    MIGRATION_MODULES = {
        "auth": "my_app.migrations_auth",
    }

   The key (``"auth"``) of ``MIGRATION_MODULES`` is the name (app_label) of the library/app, 
   and the value is package/folder to store the migration files for this library/app.

   **Note**: this value will supercede/shield the origirnal migrations folder in the library/app 
   (if it already uses django migrations), i.e., ``django.contrib.auth.migrations``.

2. Next, run ``manage.py makemigrations auth`` and ``manage.py migrate auth`` 
   to migrate the existing model as if for the first time (no matter whether the model used migrations before).
   A new migration file ``0001_initial.py`` should be generated in the specified folder.
   If the database table is already created for the model, no actual migrations will be applied.

3. Add a ``SortedOneToManyField`` named ``items`` to the ``User`` model using the helper function::
    
    inject_extra_field_to_model(User, 'items', SortedOneToManyField(Item, related_name='owner'))

4. Run ``manage.py makemigrations auth`` and ``manage.py migrate auth`` again to create the 
   intermediary table (``auth_user_items`` by default).

That's it! Now ``user.items`` and ``item.owner`` are available as if you defined the 
``items`` field in the ``User`` model source code.

Test
====
Run ``python manage.py test tests``

+ ``test_project`` contains the django project ``settings.py``
+ ``tests`` folder contains all the testcases
+ Only tested with django 1.8 + python 3.4


TODO
====

+ Add more tests, documentation and examples
+ ...
