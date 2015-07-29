=====================
django-sortedone2many
=====================

``sortedone2many`` provides a ``SortedOneToManyField`` that establishes a 
one-to-many relation (which can also remember the order of related objects).

Depends on ``SortedManyToManyField`` from the great library [django-sortedm2m]
(https://github.com/gregmuellegger/django-sortedm2m) (check it out!).

Usecases
========

The ``OneToMany`` relationship has been long missing from django ORM. 
Nevertheless, ``OneToMany`` may be needed in many cases as 
it provides better **semantics**, **readability** and **extensibility** than ``ForeignKey`` 
or other workarounds ([this blog explains it nicely](http://blog.amir.rachum.com/blog/2013/06/15/a-case-for-a-onetomany-relationship-in-django/)).

Sorting or reordering related objects in ``OneToMany`` or ``ManyToMany`` relations is also 
a strong need sometimes, where ``SortedManyToManyField`` can come in handy.

Imagine that you have a ``Category`` model and an ``Item`` model. 
Each item belongs to only one category, and each category has an ordered list of items. 
To address this need, you can simply add a ``SortedOneToManyField`` (pointed to ``Item``)
to the ``Category`` model.


Usage
=====

Just like ``SortedManyToManyField``:

    from django.db import models
    from sortedone2many.fields import SortedOneToManyField
    
    class Item(models.Model):
        name = models.CharField(max_length=50)
    
    class Category(models.Model):
        name = models.CharField(max_length=50)
        items = SortedOneToManyField(Item, sorted=True, blank=True)

In this case, ``category.items`` is the manager for related ``Item`` objects (the same as
the normal ``ManyToManyField``, e.g. ``category.items.add(new_item)``),
while ``item.category`` is an instance (not manager) of ``Category`` (similar 
to a ``OneToOneField``, e.g., ``item.category.name``).

Add ``sortedm2m`` to your INSTALLED_APPS settings to use the custom widget 
provided by ``SortedManyToManyField``, which can be used to sort
the selected items. It renders a list of checkboxes that can be sorted by
drag'n'drop.


``SortedOneToManyField``
------------------------
Similar to ``SortedManyToManyField``, 
it uses an intermediary model that holds a ForeignKey field pointed at
the model on the forward side of the relation, a OneToOneField field
pointed at the model on the remote side (to ensure each remote object
only relates to a unique forward object), and another field storing the
sort value (to remember to orders of the remote objects).


``SortedOneToManyField`` accepts a boolean ``sorted`` attribute which specifies if relation is
ordered or not. Default is set to ``True``.


Refer to [django-sortedm2m](https://github.com/gregmuellegger/django-sortedm2m)
for more details.


``OneToManyRelatedObjectDescriptor``
------------------------------------

This library also implements a ``OneToManyRelatedObjectDescriptor``,
which is an accessor to the related object (not the manager) on the 
reverse side of a one-to-many relation.

In the example::

    class Category(models.Model):
        items = SortedOneToManyField(Item, sorted=True)

``item.category`` is a OneToManyRelatedObjectDescriptor instance.

It behaves similar to a ``SingleRelatedObjectDescriptor`` as it directly
exposes the related object, but underneath it uses the ``manager`` of
the many-to-many intermediary model (similar to the
``ManyRelatedObjectsDescriptor``).
    
    
TODO
====
+ *Incomplete, untested, bugs may occur!*
+ Add tests, examples, and complete the package
+ ...
