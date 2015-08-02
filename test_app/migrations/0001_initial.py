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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategoryFixed',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'fixed categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CategorySelf',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('items', sortedone2many.fields.SortedOneToManyField(related_name='category', to='test_app.CategorySelf', blank=True, help_text=None)),
            ],
            options={
                'verbose_name_plural': 'self categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='categoryfixed',
            name='items',
            field=sortedone2many.fields.SortedOneToManyField(to='test_app.Item', blank=True, help_text=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='items',
            field=sortedone2many.fields.SortedOneToManyField(to='test_app.Item', blank=True, help_text=None),
            preserve_default=True,
        ),
    ]
