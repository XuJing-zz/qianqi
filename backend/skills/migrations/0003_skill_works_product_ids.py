
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0002_skill_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='works_product_ids',
            field=models.JSONField(blank=True, default=list, verbose_name='勾选代表作(本人作品id列表)'),
        ),
    ]
