
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0004_skill_body'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='difficulty',
            field=models.CharField(blank=True, max_length=20, verbose_name='技艺难度等级'),
        ),
    ]
