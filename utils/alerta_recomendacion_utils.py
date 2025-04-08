import pandas as pd
from config import engine
from datetime import datetime
from .miscelanea_utils import format_importe, mandar_correo
from .consultasbd_utils import (db_get_user_id_by_email, db_get_alerta_by_user_id, db_get_top3_recomendaciones_by_user_id, db_get_recomendaciones_by_user_id_and_recomendacion,
db_update_instancia_from_recomendacion_by_user_id_and_recomendacion, db_create_recomendacion_with_user_id_and_recomendacion, db_get_users, db_get_alerta_licitacion_by_alerta_id_and_licit_id,
db_create_alerta_licitacion_by_all)


def get_alertas(email):
    """
    Obtiene las alertas configuradas por un usuario específico.

    Args:
        email (str): Dirección de correo electrónico del usuario.

    Returns:
        list: Una lista de diccionarios con las alertas del usuario.
              Cada diccionario contiene los detalles de una alerta,
              incluyendo los importes formateados con separadores de miles.
    """

    # Si no se proporciona un email, retornar una lista vacía
    if email is None:
        return []

    try:
        print(email)
        user_id = db_get_user_id_by_email(email)
        print(user_id)
        # Si no se encuentra el usuario, retornar una lista vacía
        if not user_id:
            return []

        # Consultar las alertas asociadas al usuario
        alertas = db_get_alerta_by_user_id(user_id)
        print(alertas)
        # Formatear los importes (importe1 e importe2) con separadores de miles
        # y retornar una lista de diccionarios con los detalles de cada alerta
        return [
            {
                **dict(alerta),  # Convertir la fila de la base de datos en un diccionario
                'importe1': format_importe(alerta.importe1),  # Formatear importe1
                'importe2': format_importe(alerta.importe2)   # Formatear importe2
            }
            for alerta in alertas
        ]

    except Exception as e:
        # En caso de error, imprimir el mensaje de error y retornar una lista vacía
        print(f"Error al obtener alertas: {str(e)}")
        return []

def mandar_alertas():
    """
    Envía alertas personalizadas a los usuarios basadas en sus configuraciones de alertas.

    Proceso:
        1. Obtiene todos los usuarios registrados.
        2. Para cada usuario, obtiene sus alertas configuradas.
        3. Construye consultas dinámicas basadas en los filtros de cada alerta (CPV, importe, fechas, etc.).
        4. Busca licitaciones que coincidan con los filtros de la alerta.
        5. Si se encuentran licitaciones nuevas que no han sido enviadas previamente, construye un correo electrónico con los detalles de las licitaciones y lo envía al usuario.
        6. Registra las licitaciones enviadas para evitar duplicados en futuras alertas.

    Nota:
        - Las alertas se envían solo si hay licitaciones nuevas que coincidan con los criterios del usuario.
        - El cuerpo del correo incluye una descripción de la alerta y los detalles de las licitaciones encontradas.
    """
    users = db_get_users()
    for id_user, email, password in users:
        # Obtener las alertas del usuario actual
        alertas_de_user = db_get_alerta_by_user_id(id_user)
        if alertas_de_user:
            for alerta in alertas_de_user:
                id_alerta, id_usuario, cpv, contrato, palabra_clave, fecha1, fecha2, importe1, importe2 = alerta
                if fecha1 == '0000-00-00 00:00:00':
                    fecha1 = ""
                if fecha2 == '0000-00-00 00:00:00':
                    fecha2 = ""
                alerta_string = ""
                query = f"""
                        SELECT * FROM (
                            (SELECT * FROM licitacion WHERE Fecha_actualización >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) AND Fecha_de_presentación_de_ofertas IS NULL AND
                                Fecha_de_presentación_de_solicitudes_de_participacion IS NULL)
                            UNION
                            (SELECT * FROM licitacion WHERE (Fecha_de_presentación_de_ofertas IS NOT NULL AND Fecha_de_presentación_de_ofertas >= CURDATE()) OR
                                (Fecha_de_presentación_de_solicitudes_de_participacion IS NOT NULL AND Fecha_de_presentación_de_solicitudes_de_participacion >= CURDATE()))
                            ) AS subconsulta1
                        WHERE Vigente_Anulada_Archivada = 'Vigente' AND (Estado = 'Anuncio previo' OR Estado = 'En plazo')
                    """
                if cpv:
                    query += f" AND (CPV LIKE '%%{cpv}%%' AND CPV REGEXP CONCAT('(^|;)', '{cpv}'))"
                    alerta_string += f"CPV: {cpv} "
                if importe1:
                    query += f" AND Valor_estimado_del_contrato >= '{importe1}'"
                    importe1_formateado = f"{int(importe1):,}".replace(",", ".")  # Formatear con puntos
                    alerta_string += f"IMPORTE MÍNIMO: {importe1_formateado} "
                if fecha1:
                    if isinstance(fecha1, str):
                        fecha1_obj = datetime.strptime(fecha1, "%Y-%m-%d")
                        fecha1_sql = fecha1_obj.strftime("%Y-%m-%d")
                        fecha1 = fecha1_sql
                    query += f" AND Fecha_de_presentación_de_ofertas >= '{fecha1}'"
                    alerta_string += f"FECHA MÍNIMA PRESENTACIÓN OFERTAS: {fecha1} "
                if contrato:
                    query += f" AND Tipo_de_contrato = '{contrato}'"
                    alerta_string += f"TIPO DE CONTRATO: {contrato} "
                if palabra_clave:
                    query += f"""
                        AND (Objeto_del_Contrato LIKE '%%{palabra_clave}%%' COLLATE utf8mb4_unicode_ci OR
                        Órgano_de_Contratación LIKE '%%{palabra_clave}%%' COLLATE utf8mb4_unicode_ci)
                    """
                    alerta_string += f"PALABRA CLAVE: {palabra_clave} "
                if importe2:
                    query += f" AND Valor_estimado_del_contrato <= '{importe2}'"
                    importe2_formateado = f"{int(importe2):,}".replace(",", ".")  # Formatear con puntos
                    alerta_string += f"IMPORTE MÁXIMO {importe2_formateado} "
                if fecha2:
                    if isinstance(fecha2, str):
                        fecha2_obj = datetime.strptime(fecha2, "%Y-%m-%d")
                        fecha2_sql = fecha2_obj.strftime("%Y-%m-%d")
                        fecha2 = fecha2_sql
                    query += f" AND Fecha_de_presentación_de_ofertas <= '{fecha2}'"
                    alerta_string += f"FECHA MÍNIMA PRESENTACIÓN OFERTAS: {fecha2} "
                with engine.connect() as conn:
                    # Seleccionar las licitaciones que coincidan con los datos de la alerta
                    licitaciones = pd.read_sql(query, conn)
                # Crear el cuerpo del correo
                body = f"""
                    <div style="font-family: Arial, sans-serif; text-align: center; margin: 0 20px;"> <!-- Margen pequeño para móviles -->
                        <h1 style="font-size: 24px; color: #333;">¡Hola de nuevo, {email}!</h1>
                        <p style="font-size: 16px; color: #333;">
                            Estas son las últimas <b>licitaciones</b> publicadas que coinciden con tu siguiente alerta:
                        </p>
                        <p style="font-size: 14px; color: #333;">
                            {alerta_string}
                        </p>
                    </div>
                    """
                hay_minimo_una_licitacion = False
                # Obtener detalles de cada licitación asociada
                for index, row in licitaciones.iterrows():
                    licitacion_ya_alertada = db_get_alerta_licitacion_by_alerta_id_and_licit_id(id_alerta, row['ID'])
                    if not licitacion_ya_alertada:
                        if not hay_minimo_una_licitacion:
                            contador = 1
                        hay_minimo_una_licitacion = True
                        # Comprobar si hay valores nulos
                        fecha_limite = row['Fecha_de_presentación_de_ofertas'] or 'No disponible'
                        organo_contratacion = row['Órgano_de_Contratación'] or 'No disponible'
                        importe = row['Valor_estimado_del_contrato'] or 'No disponible'
                        # Construir una representación de la licitación en el correo
                        body += f"""
                            <div style="background-color: #f9f9f9; color: #333; border-radius: 8px; padding: 15px; margin: 0 10%; margin-bottom: 1.5em; max-width: 800px; margin-left: auto; margin-right: auto;">
                                <p><b>{contador}. {row['Objeto_del_Contrato']}</b></p>
                                <ul style="list-style-type: disc; padding-left: 20px;">
                                    <li><b>Fecha límite:</b> {fecha_limite}</li>
                                    <li><b>Órgano de contratación:</b> {organo_contratacion}</li>
                                    <li><b>Importe:</b> {importe} €</li>
                                    <a href='{row['Link_licitación']}' style="color: #007BFF; text-decoration: none;">Más información</a>
                                </ul>
                            </div>
                        """
                        # Asignar la licitacion a la alerta como ya alertada para evitar alertas redundantes
                        db_create_alerta_licitacion_by_all(id_alerta, row['ID'])
                if hay_minimo_una_licitacion:
                    asunto = "Nuevas licitaciones de interés"
                    mandar_correo(body, asunto, email)

def obtener_recomendaciones_principales(email):
    """
    Obtiene las tres principales recomendaciones configuradas por un usuario específico.

    Args:
        email (str): Dirección de correo electrónico del usuario.

    Returns:
        list: Una lista de diccionarios con las principales recomendaciones del usuario.
              Cada diccionario contiene los detalles de una recomendación, incluyendo
              el nombre de la recomendación y el número de instancias asociadas.
              Si no se proporciona un email o el usuario no tiene recomendaciones,
              se retorna una lista vacía.
    """
    if email is None:
        return []
    try:
        # Obtener el ID del usuario basado en su email
        user_id = db_get_user_id_by_email(email)

        # Si no se encuentra el usuario, retornar una lista vacía
        if not user_id:
            return []

        # Consultar las recomendaciones asociadas al usuario
        # Se obtienen las 3 recomendaciones con más instancias
        recomendaciones = db_get_top3_recomendaciones_by_user_id(user_id)

        # Retornar las recomendaciones obtenidas
        return recomendaciones

    except Exception as e:
        # En caso de error, imprimir el mensaje de error y retornar una lista vacía
        print(f"Error al obtener recomendaciones principales: {str(e)}")
        return []

def agregar_o_actualizar_recomendacion(email, recomendacion):
    """
    Agrega una nueva recomendación para un usuario o actualiza las instancias de una recomendación existente.

    Args:
        email (str): Dirección de correo electrónico del usuario.
        recomendacion (str): La recomendación que se desea agregar o actualizar.

    Returns:
        None: La función no retorna ningún valor explícito. Realiza operaciones directamente en la base de datos.
    """
    # Si el usuario no está logueado (email es None), no hacer nada
    if email is None:
        return

    # Obtener el ID del usuario basado en su email
    user_id = db_get_user_id_by_email(email)
    if not user_id:
        return []

    # Verificar si la recomendación ya existe para el usuario
    recomendacion_existente = db_get_recomendaciones_by_user_id_and_recomendacion(user_id, recomendacion)

    if recomendacion_existente:  # Si ya existe, actualizar la columna 'instancias'
        db_update_instancia_from_recomendacion_by_user_id_and_recomendacion(user_id, recomendacion)
    else:  # Si no existe, insertar un nuevo registro
        db_create_recomendacion_with_user_id_and_recomendacion(user_id, recomendacion)