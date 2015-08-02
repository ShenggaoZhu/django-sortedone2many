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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='CategoryFixed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'fixed categories',
            },
        ),
        migrations.CreateModel(
            name='CategorySelf',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('items', sortedone2many.fields.SortedOneToManyField(help_text=None, related_name='category', blank=True, to='test_app.CategorySelf')),
            ],
            options={
                'verbose_name_plural': 'self categories',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='categoryfixed',
            name='items',
            field=sortedone2many.fields.SortedOneToManyField(help_text=None, blank=True, to='test_app.Item'),
        ),
        migrations.AddField(
            model_name='category',
            name='items',
            field=sortedone2many.fields.SortedOneToManyField(help_text=None, blank=True, to='test_app.Item'),
        ),
    ]
