
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='video',
            field=models.CharField(blank=True, max_length=300, verbose_name='教学视频'),
        ),
    ]
