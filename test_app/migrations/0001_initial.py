# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sortedone2many.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='CategorySelf',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('items', sortedone2many.fields.SortedOneToManyField(related_name='category', to='test_app.CategorySelf', help_text=None, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FixedCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='fixedcategory',
            name='items',
            field=sortedone2many.fields.SortedOneToManyField(to='test_app.Item', help_text=None, blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='items',
            field=sortedone2many.fields.SortedOneToManyField(to='test_app.Item', help_text=None, blank=True),
        ),
    ]
