
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='image',
            field=models.CharField(blank=True, default='', max_length=500, verbose_name='技艺图片(URL)'),
        ),
    ]
