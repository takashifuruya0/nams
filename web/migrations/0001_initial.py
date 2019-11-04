# Generated by Django 2.2.6 on 2019-10-22 06:26

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('border_loss_cut', models.FloatField(blank=True, null=True)),
                ('border_profit_determination', models.FloatField(blank=True, null=True)),
                ('memo', models.TextField(blank=True, max_length=400, null=True)),
                ('is_closed', models.BooleanField(default=False)),
                ('is_simulated', models.BooleanField()),
                ('is_nisa', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='ReasonWinLoss',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=40)),
                ('is_win', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=40)),
                ('is_trust', models.BooleanField()),
                ('market', models.CharField(blank=True, max_length=30, null=True)),
                ('industry', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StockValueData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('val_high', models.FloatField()),
                ('val_low', models.FloatField()),
                ('val_open', models.FloatField()),
                ('val_close', models.FloatField()),
                ('turnover', models.FloatField()),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Stock')),
            ],
        ),
        migrations.CreateModel(
            name='StockFinancialData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('interest_bearing_debt', models.FloatField(blank=True, null=True, verbose_name='有利子負債')),
                ('roa', models.FloatField(blank=True, null=True, verbose_name='ROA')),
                ('roe', models.FloatField(blank=True, null=True, verbose_name='ROE')),
                ('sales', models.FloatField(blank=True, null=True, verbose_name='売上高')),
                ('assets', models.FloatField(blank=True, null=True, verbose_name='総資産')),
                ('eps', models.FloatField(blank=True, null=True, verbose_name='EPS')),
                ('net_income', models.FloatField(blank=True, null=True, verbose_name='当期利益')),
                ('bps', models.FloatField(blank=True, null=True, verbose_name='BPS')),
                ('roa_2', models.FloatField(blank=True, null=True, verbose_name='総資産経常利益率')),
                ('operating_income', models.FloatField(blank=True, null=True, verbose_name='営業利益')),
                ('equity_ratio', models.FloatField(blank=True, null=True, verbose_name='自己資本比率')),
                ('capital', models.FloatField(blank=True, null=True, verbose_name='資本金')),
                ('recurring_profit', models.FloatField(blank=True, null=True, verbose_name='経常利益')),
                ('equity', models.FloatField(blank=True, null=True, verbose_name='自己資本')),
                ('pbr_f', models.FloatField(blank=True, null=True, verbose_name='PBR（実績）')),
                ('eps_f', models.FloatField(blank=True, null=True, verbose_name='EPS（会社予想）')),
                ('market_value', models.FloatField(blank=True, null=True, verbose_name='時価総額')),
                ('per_f', models.FloatField(blank=True, null=True, verbose_name='PER（会社予想）')),
                ('dividend_yield', models.FloatField(blank=True, null=True, verbose_name='配当利回り（会社予想）')),
                ('bps_f', models.FloatField(blank=True, null=True, verbose_name='BPS実績')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Stock')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=datetime.datetime.now)),
                ('is_nisa', models.BooleanField(default=False)),
                ('is_buy', models.BooleanField()),
                ('is_simulated', models.BooleanField()),
                ('num', models.IntegerField()),
                ('val', models.FloatField()),
                ('commission', models.IntegerField()),
                ('chart', models.ImageField(blank=True, null=True, upload_to='images/')),
                ('entry', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.Entry')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Stock')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='entry',
            name='reason_win_loss',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.ReasonWinLoss'),
        ),
        migrations.AddField(
            model_name='entry',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.Stock'),
        ),
        migrations.AddField(
            model_name='entry',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='AssetStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('buying_power', models.IntegerField()),
                ('investment', models.IntegerField()),
                ('nisa_power', models.IntegerField()),
                ('sum_stock', models.IntegerField()),
                ('sum_trust', models.IntegerField()),
                ('sum_other', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]