
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0003_skill_works_product_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='body',
            field=models.JSONField(blank=True, default=dict, verbose_name='详情正文结构'),
        ),
    ]
