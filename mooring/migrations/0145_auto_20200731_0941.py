# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2020-07-31 01:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mooring', '0144_admissionslocation_annual_admissions_more_price_info_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admissionsbooking',
            name='mobile',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]