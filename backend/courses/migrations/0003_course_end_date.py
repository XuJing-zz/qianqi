
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_course_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='end_date',
            field=models.CharField(blank=True, max_length=10, verbose_name='结课日期'),
        ),
    ]
