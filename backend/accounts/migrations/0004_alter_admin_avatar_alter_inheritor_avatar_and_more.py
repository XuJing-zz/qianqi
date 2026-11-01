
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_admin_craft_admin_honor_admin_intro_admin_level_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admin',
            name='avatar',
            field=models.TextField(blank=True, default='', verbose_name='头像'),
        ),
        migrations.AlterField(
            model_name='inheritor',
            name='avatar',
            field=models.TextField(blank=True, default='', verbose_name='头像'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.TextField(blank=True, default='', verbose_name='头像'),
        ),
    ]
