import pymysql

try:
    # 1. Conectarse al servidor MariaDB (sin base de datos específica)
    admin_conn = pymysql.connect(
        host="158.69.59.205",
        user="web250020_user",
        password="xjdldjfRDDs#4$TR#x",
        port=3306
    )
    print("¡Conexión administrativa exitosa!")

    # 2. Reiniciar completamente la base de datos
    with admin_conn.cursor() as cursor:
        cursor.execute("DROP DATABASE IF EXISTS web250020_finanzas;")
        cursor.execute("CREATE DATABASE web250020_finanzas;")
        print("Base de datos reiniciada exitosamente.")
    
    admin_conn.close()

    # 3. Verificar conexión a la nueva base de datos vacía
    app_conn = pymysql.connect(
        host="158.69.59.205",
        user="web250020_user",
        password="xjdldjfRDDs#4$TR#x",
        database="web250020_finanzas",
        port=3306
    )
    print("¡Conexión a nueva base de datos exitosa!")
    app_conn.close()

except pymysql.Error as e:
    print(f"Error de conexión: {e}")