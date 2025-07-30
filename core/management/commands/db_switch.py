from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
import re


class Command(BaseCommand):
    help = "Cambia la base de datos activa (mariadb|sqlite) actualizando la variable ACTIVE_DB del archivo .env"

    def add_arguments(self, parser):
        parser.add_argument("engine", choices=["mariadb", "sqlite"],
                            help="Base de datos que se usará por defecto")

    def handle(self, *args, **options):
        engine = options["engine"]
        env_path = Path(settings.BASE_DIR) / ".env"

        if not env_path.exists():
            raise CommandError("No se encontró el archivo .env en la raíz del proyecto")

        pattern = re.compile(r'^ACTIVE_DB=.*$', re.MULTILINE)
        content = env_path.read_text()

        if pattern.search(content):
            content = pattern.sub(f"ACTIVE_DB={engine}", content)
        else:
            # Aseguramos salto de línea al final del archivo
            if not content.endswith("\n"):
                content += "\n"
            content += f"ACTIVE_DB={engine}\n"

        env_path.write_text(content)
        self.stdout.write(self.style.SUCCESS(
            f"ACTIVE_DB actualizado a '{engine}'. Reinicia los procesos de Django para aplicar el cambio.")) 