# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Comment(models.Model):
    com_id = models.AutoField(primary_key=True)
    team_mem_id = models.IntegerField()
    mem_file_id = models.IntegerField()
    content = models.CharField(max_length=150, blank=True, null=True)
    com_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'comment'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Edition(models.Model):
    edi_id = models.AutoField(primary_key=True)
    save_date = models.DateTimeField()
    content = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=150, blank=True, null=True)
    edi_name= models.CharField(max_length=50, blank=True, null=True)
    edi_state = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'edition'


class File(models.Model):
    file_id = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=50, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=150, blank=True, null=True)
    cre_date = models.DateTimeField()
    type = models.IntegerField()
    file_state = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'file'


class MemberEdition(models.Model):
    mem_id = models.AutoField(primary_key=True)
    mem_file_id = models.IntegerField()
    edi_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'member_edition'


class MemberFile(models.Model):
    mem_file_id = models.AutoField(primary_key=True)
    team_mem_id = models.IntegerField()
    file_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'member_file'


class MemberRole(models.Model):
    mem_role_id = models.AutoField(primary_key=True)
    team_mem_id = models.IntegerField()
    role_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'member_role'


class Permission(models.Model):
    per_id = models.AutoField(primary_key=True)
    per_name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'permission'


class PermissionRole(models.Model):
    per_role_id = models.AutoField(primary_key=True)
    per_id = models.IntegerField()
    role_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'permission_role'


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'role'


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=50)
    team_state = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField()
    date = models.DateTimeField()
    what = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'team'


class TeamMember(models.Model):
    team_mem_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    team_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'team_member'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(unique=True, max_length=50, blank=True, null=True)
    password = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=50, blank=True, null=True)
    phone = models.CharField(unique=True, max_length=11, blank=True, null=True)
    icon = models.CharField(max_length=150, blank=True, null=True)
    cre_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user'


class UserEdition(models.Model):
    user_edi_id = models.AutoField(primary_key=True)
    user_file_id = models.IntegerField()
    edi_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_edition'


class UserFile(models.Model):
    user_file_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    file_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_file'
