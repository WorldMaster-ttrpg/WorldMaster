# Generated by Django 4.2.5 on 2023-10-03 21:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ResolvedRole',
            fields=[
                ('id', models.TextField(primary_key=True, serialize=False)),
                ('type', models.SlugField(choices=[('master', 'Master'), ('editor', 'Editor'), ('viewer', 'Viewer')], help_text='The role type, like owner, editor, viewer, etc', max_length=16)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.SlugField(choices=[('master', 'Master'), ('editor', 'Editor'), ('viewer', 'Viewer')], help_text='The role type, like owner, editor, viewer, etc', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='RoleTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent', models.ForeignKey(blank=True, default=None, help_text="The parent of this RoleTarget, if it's not a root", null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='roles.roletarget')),
            ],
        ),
    ]