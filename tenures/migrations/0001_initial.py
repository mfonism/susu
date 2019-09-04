# Generated by Django 2.2.4 on 2019-09-04 15:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tenures.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EsusuGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('hash_id', models.CharField(editable=False, max_length=64)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created_on'],
            },
        ),
        migrations.CreateModel(
            name='FutureTenure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='The amount of money to be saved each month per subscriber.', max_digits=9)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('will_go_live_on', models.DateTimeField(default=tenures.models.two_weeks_from_now)),
                ('esusu_group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tenures.EsusuGroup')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='LiveSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Watch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_opted_in', models.BooleanField(default=False, help_text='Indicates whether the user has opted to join the watched tenure when it eventually goes live')),
                ('tenure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watches', to='tenures.FutureTenure')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LiveTenure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, editable=False, help_text='The amount of money to be saved each month per subscriber.', max_digits=9)),
                ('live_on', models.DateTimeField(auto_now_add=True)),
                ('esusu_group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tenures.EsusuGroup')),
                ('subscribers', models.ManyToManyField(related_name='_livetenure_subscribers_+', through='tenures.LiveSubscription', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['live_on'],
            },
        ),
        migrations.AddField(
            model_name='livesubscription',
            name='tenure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='tenures.LiveTenure'),
        ),
        migrations.AddField(
            model_name='livesubscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='HistoricalTenure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, help_text='The amount of money that was saved each month per subscriber.', max_digits=9)),
                ('live_on', models.DateTimeField()),
                ('dissolved_on', models.DateTimeField(blank=True, null=True)),
                ('esusu_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historical_tenures', to='tenures.EsusuGroup')),
                ('subscribers', models.ManyToManyField(related_name='_historicaltenure_subscribers_+', through='tenures.HistoricalSubscription', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['dissolved_on', 'live_on'],
            },
        ),
        migrations.AddField(
            model_name='historicalsubscription',
            name='tenure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='tenures.HistoricalTenure'),
        ),
        migrations.AddField(
            model_name='historicalsubscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='futuretenure',
            name='watchers',
            field=models.ManyToManyField(related_name='_futuretenure_watchers_+', through='tenures.Watch', to=settings.AUTH_USER_MODEL),
        ),
    ]
