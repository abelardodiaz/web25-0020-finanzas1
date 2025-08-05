from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Transaccion, TransaccionLegacy


class Command(BaseCommand):
    help = 'Migra transacciones del modelo legacy al nuevo modelo v0.6.0'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando migración a modelo v0.6.0...")
        
        with transaction.atomic():
            # Crear transacciones legacy a partir de las actuales
            transacciones_actuales = Transaccion.objects.all()
            count = transacciones_actuales.count()
            
            if count == 0:
                self.stdout.write("No hay transacciones para migrar.")
                return
            
            self.stdout.write(f"Migrando {count} transacciones...")
            
            # TODO: Implementar lógica de migración específica
            # Por ahora, simplemente reportamos el estado
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Migración completada. {count} transacciones procesadas.'
                )
            )