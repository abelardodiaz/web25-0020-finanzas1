# Guía de Comandos para Gestión de Bases de Datos

## 🔄 Cambiar entre MariaDB y SQLite
```bash
# Cambiar a SQLite
python manage.py db_switch sqlite

# Cambiar a MariaDB
python manage.py db_switch mariadb

# Verificar BD activa
echo "from django.conf import settings; print(settings.DATABASES['default']['ENGINE'])" | python manage.py shell
```

## 📤 Importar/Exportar Datos
```bash
# Copiar MariaDB → SQLite
python manage.py db_copy --from mariadb --to sqlite

# Copiar SQLite → MariaDB
python manage.py db_copy --from sqlite --to mariadb

# Conservar datos existentes (append)
python manage.py db_copy --from mariadb --to sqlite --keep
```

## 🛠 Mantenimiento de Esquemas
```bash
# Crear migraciones después de cambios en modelos
python manage.py makemigrations

# Aplicar migraciones a SQLite
python manage.py migrate --database=sqlite

# Aplicar migraciones a MariaDB
python manage.py migrate --database=mariadb

# Verificar migraciones pendientes
python manage.py showmigrations --database=sqlite
```

## 🔍 Consultas Directas
```bash
# SQLite - Ver estructura de tabla
sqlite3 db.sqlite3 ".schema core_transaccion"

# SQLite - Últimas 5 transacciones
sqlite3 db.sqlite3 "SELECT id, fecha, descripcion, monto FROM core_transaccion ORDER BY id DESC LIMIT 5;"

# MariaDB - Shell interactivo
python manage.py dbshell --database=mariadb

# MariaDB - Consulta directa
echo "SELECT * FROM core_transaccion WHERE id=439;" | python manage.py dbshell --database=mariadb
```

## 🚨 Solución de Problemas
```bash
# Error "No such table" en SQLite
python manage.py makemigrations
python manage.py migrate --database=sqlite

# Datos no visibles después de copiar
python manage.py db_copy --from mariadb --to sqlite  # Forzar recopia
grep ACTIVE_DB .env  # Verificar BD activa

# Error en migraciones duplicadas
rm core/migrations/00XX_conflictivo.py  # Eliminar migración conflictiva
python manage.py makemigrations  # Regenerar
```

## 💾 Backup y Restauración
```bash
# Backup SQLite
cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3

# Restaurar SQLite
cp db_backup_20230715.sqlite3 db.sqlite3

# Backup MariaDB (requiere mysqldump)
mysqldump -u [user] -p[pass] [dbname] > backup.sql
```

> **Notas**:  
> - Todos los comandos se ejecutan en el directorio del proyecto  
> - Requieren entorno virtual activado  
> - Cambios en `.env` necesitan reinicio de procesos Django  
> - `db_copy` incluye automáticamente `flush` + `migrate` en destino