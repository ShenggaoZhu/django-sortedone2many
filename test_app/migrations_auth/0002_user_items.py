# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedone2many.fields


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='items',
            field=sortedone2many.fields.SortedOneToManyField(help_text=None, related_name='owner', to='test_app.Item'),
        ),
    ]
