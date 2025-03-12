from config import engine
from sqlalchemy import text
from datetime import datetime
import pandas as pd
from flask import jsonify

def db_get_user_id_by_email(email):
    """
    Obtiene el ID de un usuario basado en su email.

    Args:
        email (str): Dirección de correo electrónico del usuario.

    Returns:
        El ID del usuario si existe, o None si no se encuentra.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        user = conn.execute(
            text("SELECT id FROM usuarios WHERE email = :email"),
            {'email': email}
        ).fetchone()

        # Si se encuentra el usuario, devuelve su ID; de lo contrario, devuelve None
        return user['id'] if user else None

def db_get_users():
    """
    Obtiene todos los usuarios de la base de datos.

    Returns:
        Una lista con todos los usuarios si existen, o None si no hay usuarios.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        users = conn.execute(
            text("SELECT * FROM usuarios")
        ).fetchall()

        # Retorna todos los usuarios si existen; de lo contrario, retorna None
        return users if users else None

def db_get_alerta_by_user_id(user_id):
    """
    Obtiene todas las alertas asociadas a un usuario específico.

    Args:
        user_id (int): ID del usuario.

    Returns:
        Una lista con las alertas del usuario si existen, o None si no hay alertas.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        alertas = conn.execute(
            text("""
                SELECT * FROM alertas
                WHERE id_usuario = :user_id
            """),
            {'user_id': user_id}
        ).fetchall()

        # Retorna las alertas si existen; de lo contrario, retorna None
        return alertas if alertas else None

def db_get_top3_recomendaciones_by_user_id(user_id):
    """
    Obtiene las 3 recomendaciones principales de un usuario, ordenadas por el número de instancias en orden descendente.

    Args:
        user_id (int): ID del usuario.

    Returns:
        Una lista con las 3 recomendaciones principales si existen, o None si no hay recomendaciones.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        recomendaciones = conn.execute(
            text("""
                SELECT recomendacion, instancias
                FROM recomendaciones
                WHERE id_usuario = :user_id
                ORDER BY instancias DESC
                LIMIT 3
            """),
            {'user_id': user_id}
        ).fetchall()

        # Retorna las recomendaciones si existen; de lo contrario, retorna None
        return recomendaciones if recomendaciones else None

def db_get_recomendaciones_by_user_id_and_recomendacion(user_id, recomendacion):
    """
    Verifica si una recomendación específica existe para un usuario dado.

    Args:
        user_id (int): ID del usuario.
        recomendacion (str): La recomendación a verificar.

    Returns:
        True si la recomendación existe; de lo contrario, retorna None.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        recomendacion_existente = conn.execute(
            text("SELECT 1 FROM recomendaciones WHERE id_usuario = :user_id AND recomendacion = :recomendacion"),
            {'user_id': user_id, 'recomendacion': recomendacion}
        ).fetchone()

        # Retorna True si existe la recomendación; de lo contrario, retorna None
        return recomendacion_existente if recomendacion_existente else None

def db_update_instancia_from_recomendacion_by_user_id_and_recomendacion(user_id, recomendacion):
    """
    Incrementa el contador de instancias para una recomendación específica de un usuario.

    Args:
        user_id (int): ID del usuario.
        recomendacion (str): La recomendación a actualizar.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("UPDATE recomendaciones SET instancias = instancias + 1 WHERE id_usuario = :user_id AND recomendacion = :recomendacion"),
            {'user_id': user_id, 'recomendacion': recomendacion}
        )

def db_create_recomendacion_with_user_id_and_recomendacion(user_id, recomendacion):
    """
    Crea una nueva recomendación para un usuario específico.

    Args:
        user_id (int): ID del usuario.
        recomendacion (str): La recomendación a crear.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("INSERT INTO recomendaciones (id_usuario, recomendacion, instancias) VALUES (:user_id, :recomendacion, 0)"),
            {'user_id': user_id, 'recomendacion': recomendacion}
        )

def db_delete_alerta_by_alerta_id(alerta_id):
    """
    Elimina una alerta específica basada en su ID.

    Args:
        alerta_id (int): ID de la alerta a eliminar.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("DELETE FROM alertas WHERE id = :alerta_id"),
            {'alerta_id': alerta_id}
        )

def db_delete_alerta_licitacion_by_alerta_id(alerta_id):
    """
    Elimina una relación entre una alerta y una licitación basada en el ID de la alerta.

    Args:
        alerta_id (int): ID de la alerta a eliminar.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("DELETE FROM alerta_licitacion WHERE id_alerta = :alerta_id"),
            {'alerta_id': alerta_id}
        )

def db_get_alerta_by_all(user_id, cpv_search, contrato, palabra_clave, fecha1, fecha2, importe1, importe2):
    """
    Verifica si existe una alerta que coincida con todos los filtros proporcionados.

    Args:
        user_id (int): ID del usuario.
        cpv_search (str): Código CPV buscado.
        contrato (str): Tipo de contrato.
        palabra_clave (str): Palabra clave.
        fecha1 (str): Fecha mínima.
        fecha2 (str): Fecha máxima.
        importe1 (int): Importe mínimo.
        importe2 (int): Importe máximo.

    Returns:
        True si existe la alerta; de lo contrario, retorna None.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        result = conn.execute(
            text("""
                SELECT 1 FROM alertas
                WHERE id_usuario = :user_id
                  AND cpv = :cpv
                  AND contrato = :contrato
                  AND palabra_clave = :palabra_clave
                  AND fecha1 = :fecha1
                  AND fecha2 = :fecha2
                  AND importe1 = :importe1
                  AND importe2 = :importe2
            """),
            {
                'user_id': user_id,
                'cpv': cpv_search,
                'contrato': contrato,
                'palabra_clave': palabra_clave,
                'fecha1': fecha1,
                'fecha2': fecha2,
                'importe1': importe1,
                'importe2': importe2
            }
        ).fetchone()

        # Retorna True si existe la alerta; de lo contrario, retorna None
        return result if result else None

def db_create_alerta_by_all(user_id, cpv_search, contrato, palabra_clave, fecha1, fecha2, importe1, importe2):
    """
    Crea una nueva alerta con todos los filtros proporcionados.

    Args:
        user_id (int): ID del usuario.
        cpv_search (str): Código CPV buscado.
        contrato (str): Tipo de contrato.
        palabra_clave (str): Palabra clave.
        fecha1 (str): Fecha mínima.
        fecha2 (str): Fecha máxima.
        importe1 (int): Importe mínimo.
        importe2 (int): Importe máximo.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("""
                INSERT INTO alertas (id_usuario, cpv, contrato, palabra_clave, fecha1, fecha2, importe1, importe2)
                VALUES (:user_id, :cpv, :contrato, :palabra_clave, :fecha1, :fecha2, :importe1, :importe2)
            """),
            {
                'user_id': user_id,
                'cpv': cpv_search,
                'contrato': contrato,
                'palabra_clave': palabra_clave,
                'fecha1': fecha1,
                'fecha2': fecha2,
                'importe1': importe1,
                'importe2': importe2
            }
        )

def db_get_last_alerta_id():
    """
    Obtiene el ID de la última alerta creada.

    Returns:
        El ID de la última alerta si existe, o None si no hay alertas.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        id_alerta = conn.execute(
            text("SELECT id FROM alertas ORDER BY id DESC LIMIT 1")
        ).fetchone()

        # Retorna el ID de la última alerta si existe; de lo contrario, retorna None
        return id_alerta if id_alerta else None

def db_get_alerta_licitacion_by_alerta_id_and_licit_id(id_alerta, id_licitacion):
    """
    Verifica si existe una relación específica entre una alerta y una licitación.

    Args:
        id_alerta (int): ID de la alerta.
        id_licitacion (int): ID de la licitación.

    Returns:
        True si la relación existe; de lo contrario, retorna None.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        licitacionya = conn.execute(
            text("SELECT 1 FROM alerta_licitacion WHERE id_alerta = :id_alerta AND id_licitacion = :id_licitacion"),
            {'id_alerta': id_alerta, 'id_licitacion': id_licitacion}
        ).fetchone()

        # Retorna True si la relación existe; de lo contrario, retorna None
        return licitacionya if licitacionya else None

def db_create_alerta_licitacion_by_all(id_alerta, id_lici):
    """
    Crea una nueva relación entre una alerta y una licitación.

    Args:
        id_alerta (int): ID de la alerta.
        id_lici (int): ID de la licitación.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("INSERT INTO alerta_licitacion (id_alerta, id_licitacion) values (:id_alerta, :id_lici)"),
            {'id_alerta': id_alerta, 'id_lici': id_lici})

def db_update_email_from_user_by_email(old_email, new_email):
    """
    Actualiza el correo electrónico de un usuario basado en su correo anterior.

    Args:
        old_email (str): Correo electrónico anterior del usuario.
        new_email (str): Nuevo correo electrónico del usuario.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("UPDATE usuarios SET email = :new_email WHERE email = :old_email"),
            {"old_email": old_email, "new_email": new_email}
        )

def db_update_password_from_user_by_email(email, password):
    """
    Actualiza la contraseña de un usuario basado en su correo electrónico.

    Args:
        email (str): Correo electrónico del usuario.
        password (str): Nueva contraseña del usuario ya encriptada.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("UPDATE usuarios SET password = :password WHERE email = :email"),
            {"email": email, "password": password}
        )

def db_delete_user(email):
    """
    Elimina un usuario y sus alertas asociadas basado en su correo electrónico.

    Args:
        email (str): Correo electrónico del usuario a eliminar.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        user_id = conn.execute(
            text("SELECT id FROM usuarios WHERE email = :email"),
            {"email": email}
        )
        conn.execute(
            text("DELETE FROM usuarios WHERE email = :email"),
            {"email": email}
        )
        conn.execute(
            text("DELETE FROM alertas WHERE id_usuario = :user_id"),
            {"user_id": user_id}
        )

def db_get_user_by_email(email):
    """
    Obtiene los datos de un usuario basado en su correo electrónico.

    Args:
        email (str): Correo electrónico del usuario.

    Returns:
        Los datos del usuario si existe; de lo contrario, retorna None.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        user = conn.execute(
            text("SELECT * FROM usuarios WHERE email = :email"),
            {'email': email}
        ).fetchone()

        # Retorna los datos del usuario si existe; de lo contrario, retorna None
        return user if user else None

def db_create_user_by_all(email, password):
    """
    Crea un nuevo usuario con el correo electrónico y la contraseña proporcionados.

    Args:
        email (str): Correo electrónico del nuevo usuario.
        password (str): Contraseña del nuevo usuario ya encriptada.
    """
    with engine.connect() as conn:
        # Ejecutar la consulta SQL
        conn.execute(
            text("INSERT INTO usuarios (email, password) VALUES (:email, :password)"),
            {"email": email, "password": password}
        )

def db_get_datos(tabla, page, limit, sort_by, order, cpv_search, palabra_clave, contrato, fecha1, fecha2, importe1=None, importe2=None):
    """
    Obtiene datos paginados y filtrados de una tabla específica.

    Args:
        tabla (str): Nombre de la tabla ('licitacion' o 'consulta').
        page (int): Número de página actual.
        limit (int): Número máximo de resultados por página.
        sort_by (str): Campo por el cual ordenar los resultados.
        order (str): Orden de los resultados ('ASC' o 'DESC').
        cpv_search (str): Código CPV para filtrar.
        palabra_clave (str): Palabra clave para filtrar.
        contrato (str): Tipo de contrato para filtrar.
        fecha1 (str): Fecha mínima para filtrar.
        fecha2 (str): Fecha máxima para filtrar.
        importe1 (int): Importe mínimo para filtrar.
        importe2 (int): Importe máximo para filtrar.

    Returns:
        Un DataFrame con los datos obtenidos.
    """
    if page == 0:
        page = 1 # Asegurarse de que la página no sea menor a 1
    offset = (page - 1) * limit  # Cálculo del desplazamiento
    if not order:
        order = 'ASC'
    if not sort_by:
        sort_by = 'Fecha_actualización'

    if tabla == 'licitacion':
        # Construir la consulta SQL para obtener los resultados
        query = f"""
            SELECT *, COUNT(*) OVER () AS total_count
            FROM (
                (SELECT * FROM {tabla} WHERE Fecha_actualización >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) AND Fecha_de_presentación_de_ofertas IS NULL AND
                    Fecha_de_presentación_de_solicitudes_de_participacion IS NULL)
                UNION
                (SELECT * FROM {tabla} WHERE (Fecha_de_presentación_de_ofertas IS NOT NULL AND Fecha_de_presentación_de_ofertas >= CURDATE()) OR
                    (Fecha_de_presentación_de_solicitudes_de_participacion IS NOT NULL AND Fecha_de_presentación_de_solicitudes_de_participacion >= CURDATE()))
            ) AS subconsulta1
            WHERE Vigente_Anulada_Archivada = 'Vigente' AND (Estado = 'Anuncio previo' OR Estado = 'En plazo')
        """
    else: # tabla == 'consulta'
        query = f"""
        SELECT *, COUNT(*) OVER () AS total_count FROM consulta
        WHERE Fecha_límite_de_respuesta >= CURDATE()
            AND Vigente_Anulada_Archivada = 'Vigente'
            AND (Estado = 'Publicada')
        """
    try:
        with engine.connect() as conn:
            # Aplicar filtros dinámicamente
            if cpv_search and len(cpv_search) <= 8:
                query += f" AND (CPV LIKE '%%{cpv_search}%%' AND CPV REGEXP CONCAT('(^|;)', {cpv_search}))"
            if palabra_clave:
                query += f""" # compruebo cualquier aparición de la palabra clave
                    AND (Objeto_del_Contrato LIKE '%%{palabra_clave}%%' COLLATE utf8mb4_unicode_ci OR
                    Órgano_de_Contratación LIKE '%%{palabra_clave}%%' COLLATE utf8mb4_unicode_ci)
                """
            if importe1:
                query += f" AND Valor_estimado_del_contrato >= {importe1}"
            if importe2:
                query += f" AND Valor_estimado_del_contrato <= {importe2}"
            if contrato:
                query += f" AND Tipo_de_contrato = '{contrato}'"
            if fecha1:
                fecha1_obj = datetime.strptime(fecha1, "%Y-%m-%d")
                fecha1_sql = fecha1_obj.strftime("%Y-%m-%d")
                query += f" AND Fecha_de_presentación_de_ofertas >= '{fecha1_sql}'"
            if fecha2:
                fecha2_obj = datetime.strptime(fecha2, "%Y-%m-%d")
                fecha2_sql = fecha2_obj.strftime("%Y-%m-%d")
                query += f" AND Fecha_de_presentación_de_ofertas <= '{fecha2_sql}'"

            # Añadir paginación y ordenamiento
            query += f" ORDER BY {sort_by} {order} LIMIT {limit} OFFSET {offset}"

            # Ejecutar consultas y convertir a dataframe
            df = pd.read_sql(query, conn)
        return df

    except Exception as e:
        print(f"Error al obtener datos de la tabla {tabla}: {str(e)}")
        return jsonify({"error": str(e)}), 500

def db_get_cpvs():
    """
    Obtiene todos los códigos CPV y sus nombres.

    Returns:
        Un DataFrame con los códigos CPV y sus nombres.
    """
    with engine.connect() as conn:
        cpv_query = "SELECT numero, nombre FROM cpvs"
        cpv_df = pd.read_sql(cpv_query, conn)
        return cpv_df

