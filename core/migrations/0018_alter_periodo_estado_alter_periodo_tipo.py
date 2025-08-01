# Generated by Django 5.2.4 on 2025-07-29 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_periodo_generado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='periodo',
            name='estado',
            field=models.CharField(blank=True, choices=[('PENDIENTE', 'Pendiente'), ('PAGADO', 'Pagado'), ('CANCELADO', 'Cancelado')], default='PENDIENTE', max_length=10),
        ),
        migrations.AlterField(
            model_name='periodo',
            name='tipo',
            field=models.CharField(blank=True, choices=[('TDC', 'Tarjeta de Crédito'), ('SERV', 'Servicio'), ('DEB', 'Débito'), ('EFE', 'Efectivo')], default=None, max_length=10, null=True),
        ),
    ]
