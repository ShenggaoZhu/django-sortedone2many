# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='fk',
            field=models.ForeignKey(blank=True, null=True, to='test_app.Category'),
        ),
    ]
