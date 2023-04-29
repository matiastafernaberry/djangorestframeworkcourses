# Generated by Django 4.2 on 2023-04-29 22:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LittleLemonDRF', '0003_alter_cart_unique_together_order_orderitem'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.BooleanField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LittleLemonDRF.order'),
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
    ]