
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0006_skill_attachments'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='cautions',
            field=models.TextField(blank=True, verbose_name='注意事项'),
        ),
        migrations.AddField(
            model_name='skill',
            name='hard_points',
            field=models.TextField(blank=True, verbose_name='制作难点'),
        ),
        migrations.AddField(
            model_name='skill',
            name='raw_materials',
            field=models.TextField(blank=True, verbose_name='原材料清单'),
        ),
        migrations.AddField(
            model_name='skill',
            name='tools',
            field=models.TextField(blank=True, verbose_name='专用工具'),
        ),
    ]
