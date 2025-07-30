from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import tempfile
import os


class Command(BaseCommand):
    help = (
        "Copia todos los datos de una base de datos a otra (mariadb ↔ sqlite) "
        "usando los serializadores de Django."
    )

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="src", required=True,
                            choices=["mariadb", "sqlite"],
                            help="Alias de la base de datos origen")
        parser.add_argument("--to", dest="dst", required=True,
                            choices=["mariadb", "sqlite"],
                            help="Alias de la base de datos destino")
        parser.add_argument("--keep", action="store_true",
                            help="Si se indica, no se vacía la base de destino antes de importar")

    def handle(self, *args, **options):
        src = options["src"]
        dst = options["dst"]

        if src == dst:
            raise CommandError("Las bases de datos origen y destino deben ser distintas.")

        self.stdout.write(self.style.NOTICE(f"Dump de datos desde '{src}'…"))
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            dump_path = tmp.name

        try:
            # Volcar datos a un archivo temporal
            with open(dump_path, "w", encoding="utf-8") as dump_file:
                call_command(
                    "dumpdata",
                    "--natural-foreign",
                    "--natural-primary",
                    "--indent", "2",
                    "--database", src,
                    stdout=dump_file
                )

            if not options["keep"]:
                self.stdout.write(self.style.NOTICE(f"Vaciando '{dst}'…"))
                call_command("flush", "--database", dst, "--noinput")
                
                # Añadir migraciones para crear tablas
                self.stdout.write(self.style.NOTICE(f"Creando esquema en '{dst}'…"))
                call_command("migrate", "--database", dst, "--noinput")

            self.stdout.write(self.style.NOTICE(f"Cargando datos en '{dst}'…"))
            call_command("loaddata", dump_path, "--database", dst)

            self.stdout.write(self.style.SUCCESS("Proceso completado correctamente."))
        finally:
            os.remove(dump_path) 