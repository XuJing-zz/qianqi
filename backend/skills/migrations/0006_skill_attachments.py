
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0005_skill_difficulty'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='attachments',
            field=models.JSONField(blank=True, default=list, verbose_name='附件文档'),
        ),
    ]
