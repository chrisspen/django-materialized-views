# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MaterializedViewControl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, editable=False)),
                ('app_label', models.CharField(max_length=250, null=True, editable=False, blank=True)),
                ('enabled', models.BooleanField(default=True, help_text='If checked, this model will be routinely updated.')),
                ('stripable', models.BooleanField(default=False, help_text='If checked, implies insert/update/delete methods accept\n            a valid stripe parameter that tell them to segment query during\n            multiprocessing.')),
                ('include_in_batch', models.BooleanField(default=True, help_text='If checked, will be materialized when the\n            update_materialized_views command is run with no model name\n            specified. This is useful when a specific model is especially\n            long-running or should be rarely or conditionally run or otherwise\n            not run with the other views.')),
            ],
            options={
                'verbose_name': 'control',
                'verbose_name_plural': 'controls',
            },
        ),
        migrations.AlterUniqueTogether(
            name='materializedviewcontrol',
            unique_together=set([('name', 'app_label')]),
        ),
    ]
