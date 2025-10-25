# crud.py

# pip install mysql-connector-python flask flask-cors requests
import mysql.connector
from datetime import datetime

# Configurar conexión
# Los datos son: host="127.0.0.1", user="root", password="contrasena", database="dofdb", port=3306
conn = mysql.connector.connect(
    host="127.0.0.1",  # Docker expone en localhost
    user="root",
    password="contrasena",
    database="dofdb",  # Cambiado a 'dofdb'
    port=3306  # Puerto mapeado en Docker
)
cursor = conn.cursor()

# ----------------------------------------------------
## Funciones CRUD para la tabla 'summaries'
# ----------------------------------------------------

# Crear un nuevo resumen (CREATE)
def create_summary(object_type, object_id, model, model_version, lang, summary_text, confidence, created_by=None):
    """Inserta un nuevo registro de resumen en la tabla summaries."""
    sql = """
    INSERT INTO summaries (object_type, object_id, model, model_version, lang, summary_text, confidence, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    # NOTA: created_at se establece automáticamente por la base de datos (DEFAULT CURRENT_TIMESTAMP)
    
    # Asegúrate de que object_type sea un valor válido para ENUM: 'publication','section','item','chunk'
    # object_id debe ser un entero
    # confidence debe ser un decimal (p.ej., 0.95)
    
    values = (object_type, object_id, model, model_version, lang, summary_text, confidence, created_by)
    
    try:
        cursor.execute(sql, values)
        conn.commit()
        print(f"Resumen creado exitosamente para object_id: {object_id}")
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error al crear resumen: {err}")
        conn.rollback()
        return None

# Leer todos los resúmenes (READ)
def read_summaries():
    """Recupera todos los registros de la tabla summaries."""
    cursor.execute("SELECT id, object_type, object_id, model, lang, confidence FROM summaries")
    # Para evitar cargar todo el texto largo (summary_text) en la impresión inicial
    return cursor.fetchall()

# Leer un resumen por su ID
def read_summary_by_id(summary_id):
    """Recupera un resumen específico por su ID."""
    cursor.execute("SELECT * FROM summaries WHERE id = %s", (summary_id,))
    return cursor.fetchone()

# Actualizar el texto del resumen y la confianza por ID (UPDATE)
def update_summary(summary_id, new_summary_text, new_confidence, new_model_version=None):
    """Actualiza el texto del resumen, la confianza y opcionalmente la versión del modelo."""
    
    sql = "UPDATE summaries SET summary_text=%s, confidence=%s"
    values = [new_summary_text, new_confidence]
    
    if new_model_version is not None:
        sql += ", model_version=%s"
        values.append(new_model_version)
        
    sql += " WHERE id=%s"
    values.append(summary_id)
    
    try:
        cursor.execute(sql, tuple(values))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Resumen con ID {summary_id} actualizado exitosamente.")
        else:
            print(f"No se encontró el Resumen con ID {summary_id} para actualizar.")
    except mysql.connector.Error as err:
        print(f"Error al actualizar resumen: {err}")
        conn.rollback()

# Eliminar un resumen por ID (DELETE)
def delete_summary(summary_id):
    """Elimina un resumen específico por su ID."""
    sql = "DELETE FROM summaries WHERE id=%s"
    try:
        cursor.execute(sql, (summary_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Resumen con ID {summary_id} eliminado exitosamente.")
        else:
            print(f"No se encontró el Resumen con ID {summary_id} para eliminar.")
    except mysql.connector.Error as err:
        print(f"Error al eliminar resumen: {err}")
        conn.rollback()

# ----------------------------------------------------
## Ejemplo de uso
# ----------------------------------------------------

print("--- 1. Creando nuevos resúmenes ---")
# Crear Resumen 1
id_resumen_1 = create_summary(
    object_type='publication',
    object_id=20250101001,
    model='GPT-4',
    model_version='1.0',
    lang='es',
    summary_text='Resumen conciso de la Publicación 001 del DOF del 1 de enero de 2025.',
    confidence=0.98,
    created_by='IA_Generator_v1'
)

# Crear Resumen 2
id_resumen_2 = create_summary(
    object_type='section',
    object_id=20250101001003,
    model='Claude-3',
    model_version='Sonnet',
    lang='en', # Ejemplo de otro idioma
    summary_text='Simple summary of Section 3 of the publication, focused on fiscal changes.',
    confidence=0.92,
    created_by='IA_Generator_v2'
)

print("\n--- 2. Leyendo todos los resúmenes ---")
all_summaries = read_summaries()
print("Resúmenes (ID, Tipo, Object ID, Modelo, Idioma, Confianza):")
for s in all_summaries:
    print(f" - {s}")

print("\n--- 3. Actualizando el Resumen 1 ---")
# Actualizar el texto y la confianza del primer resumen
update_summary(
    summary_id=id_resumen_1,
    new_summary_text='Resumen *mejorado* y más sencillo de la Publicación 001 del DOF.',
    new_confidence=0.99,
    new_model_version='1.1' # Opcional: actualizar la versión del modelo
)

print("\n--- 4. Leyendo un resumen específico y listando de nuevo ---")
summary_1_details = read_summary_by_id(id_resumen_1)
print(f"Detalles del Resumen 1 después de actualizar:\n{summary_1_details}")


# Cerrar la conexión
print("\nCerrando conexión a la base de datos.")
cursor.close()
conn.close()
