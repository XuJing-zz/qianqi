from django.db import migrations


def backfill(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    for order in Order.objects.filter(order_no='').order_by('id'):
        day = (order.order_time or order.created_at.strftime('%Y%m%d'))[:8].replace('-', '') or '20260101'
        Order.objects.filter(pk=order.pk).update(
            order_no='QQ{}{:06d}'.format(day, order.pk)
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_order_order_no_orderstatuslog'),
    ]

    operations = [
        migrations.RunPython(backfill, noop),
    ]
