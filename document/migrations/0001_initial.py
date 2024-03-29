# Generated by Django 2.2.4 on 2019-08-12 07:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MemRole',
            fields=[
                ('mem_role_id', models.AutoField(primary_key=True, serialize=False)),
                ('team_user_id', models.IntegerField()),
                ('role_id', models.IntegerField()),
            ],
            options={
                'db_table': 'mem_role',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('per_id', models.AutoField(primary_key=True, serialize=False)),
                ('per_name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'permission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PerRole',
            fields=[
                ('per_role_id', models.AutoField(primary_key=True, serialize=False)),
                ('per_id', models.IntegerField()),
                ('role_id', models.IntegerField()),
            ],
            options={
                'db_table': 'per_role',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('role_id', models.AutoField(primary_key=True, serialize=False)),
                ('role_name', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'role',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('team_id', models.AutoField(primary_key=True, serialize=False)),
                ('team_name', models.CharField(max_length=50)),
                ('team_state', models.IntegerField(blank=True, null=True)),
                ('user_id', models.IntegerField()),
                ('number', models.IntegerField()),
            ],
            options={
                'db_table': 'team',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TeamUser',
            fields=[
                ('team_user_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField()),
                ('team_id', models.IntegerField()),
            ],
            options={
                'db_table': 'team_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('password', models.CharField(max_length=20)),
                ('email', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=11, null=True, unique=True)),
                ('icon', models.CharField(blank=True, max_length=150, null=True)),
                ('cre_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'user',
                'managed': False,
            },
        ),
    ]
