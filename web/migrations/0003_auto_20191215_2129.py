# Generated by Django 2.2.6 on 2019-12-15 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20191125_2216'),
    ]

    operations = [
        migrations.CreateModel(
            name='V_Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('is_closed', models.BooleanField()),
                ('date_open', models.DateTimeField()),
                ('date_close', models.DateTimeField()),
                ('period', models.IntegerField()),
                ('buy_total', models.FloatField()),
                ('sell_total', models.FloatField()),
                ('commission', models.IntegerField()),
                ('profit', models.FloatField()),
                ('buy_num', models.IntegerField()),
                ('buy_price', models.FloatField()),
                ('sell_num', models.IntegerField()),
                ('sell_price', models.FloatField()),
            ],
            options={
                'managed': False,
                'db_table': 'v_entry',
            },
        ),
        migrations.AddField(
            model_name='reasonwinloss',
            name='description',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]