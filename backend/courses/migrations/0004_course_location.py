
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_course_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='location',
            field=models.CharField(blank=True, max_length=200, verbose_name='上课地点'),
        ),
    ]
