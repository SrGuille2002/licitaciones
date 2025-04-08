from flask import render_template, request, redirect, session, flash, Blueprint
from sqlalchemy import text
from config import engine
from datetime import datetime
from utils import get_alertas, db_delete_alerta_by_alerta_id, db_delete_alerta_licitacion_by_alerta_id, db_get_user_id_by_email, db_get_alerta_by_all, db_create_alerta_by_all, mandar_correo, db_get_last_alerta_id, db_create_alerta_licitacion_by_all

alerta_bp = Blueprint('alerta', __name__)

@alerta_bp.route('/alerta', methods=['GET'])
def alerta():
    """
    Ruta para mostrar las alertas configuradas por el usuario.

    Si el usuario está autenticado, se obtienen sus alertas desde la base de datos.
    Si no está autenticado, se muestra un mensaje en la consola y se devuelve una lista vacía.

    Returns:
        render_template: Renderiza la plantilla 'alerta.html' con las alertas del usuario.
    """

    # Verificar si el usuario está autenticado (es decir, si 'email' está en la sesión)
    if 'email' in session:
        # Obtener el email del usuario desde la sesión
        email = session['email']

        # Llamar a la función `get_alertas` para obtener las alertas del usuario
        result = get_alertas(email)
    else:
        # Si el usuario no está autenticado, imprimir un mensaje en la consola
        print("Usuario no autenticado.")

        # Devolver una lista vacía porque no hay alertas para usuarios no autenticados
        result = []

    # Renderizar la plantilla 'alerta.html' y pasarle las alertas como contexto
    return render_template('alerta.html', result=result)

@alerta_bp.route('/alerta/eliminar', methods=['POST'])
def eliminar_alerta():
    """
    Ruta para eliminar una alerta específica.

    Esta función elimina una alerta de la base de datos si el usuario está autenticado
    y se proporciona un ID de alerta válido. También elimina las relaciones asociadas
    en la tabla `alerta_licitacion`.

    Returns:
        redirect: Redirige al usuario a la página '/alerta' después de intentar eliminar la alerta.
    """

    # Verificar si el usuario está autenticado (es decir, si 'email' está en la sesión)
    if 'email' in session:
        # Obtener el ID de la alerta desde el formulario enviado por POST
        alerta_id = request.form.get('alerta_id')

        if alerta_id:
            try:
                # Eliminar la alerta de la tabla `alertas`
                db_delete_alerta_by_alerta_id(alerta_id)

                # Eliminar las relaciones asociadas en la tabla `alerta_licitacion`
                db_delete_alerta_licitacion_by_alerta_id(alerta_id)

                # Mostrar un mensaje de éxito usando Flask-Flash
                flash("Alerta eliminada con éxito.", "success")
            except Exception as e:
                # En caso de error, mostrar un mensaje de error
                flash(f"Error al eliminar la alerta: {str(e)}", "error")
        else:
            # Si no se proporciona un ID de alerta, mostrar un mensaje de error
            flash("No se pudo eliminar la alerta.", "error")
    else:
        # Si el usuario no está autenticado, mostrar un mensaje de error
        flash("Debes estar autenticado para eliminar alertas.", "error")

    # Redirigir al usuario a la página de alertas
    return redirect('/alertas/alerta')

@alerta_bp.route('/nueva_alerta', methods=['POST'])
def nueva_alerta():
    """
    Crea una nueva alerta basada en los filtros almacenados en la sesión del usuario.

    Proceso:
        1. Verifica si el usuario está autenticado (email en la sesión). Si no lo está, redirige al usuario a la página de inicio.
        2. Recupera los valores de los filtros almacenados en la sesión (CPV, importe, fechas, tipo de contrato, palabra clave,...).
        3. Construye dinámicamente una consulta SQL para buscar licitaciones que coincidan con los filtros de la alerta.
        4. Genera un mensaje descriptivo ('alerta_string') con los filtros seleccionados.
        5. Verifica si ya existe una alerta con los mismos filtros para el usuario. Si no existe, crea una nueva alerta en la base de datos.
        6. Envía un correo electrónico al usuario notificando la creación de la alerta.
        7. Asocia las licitaciones existentes que cumplen con los criterios de la alerta para no mandar futuras alertas redundantes.
        8. Redirige al usuario a la página principal de licitaciones.

    Args:
        Ninguno directamente, pero utiliza los valores almacenados en la sesión del usuario.

    Returns:
        Redirige al usuario a la página principal de licitaciones ('/datos/get_data_lici').

    Notas:
        - Los valores de importe se formatean eliminando puntos y utilizando separadores de miles.
        - Si la longitud del mensaje de la alerta es menor a 10 caracteres, se considera inválida y redirige al usuario.
        - Se utiliza una consulta SQL compleja para filtrar licitaciones vigentes y activas.
        - Las licitaciones que cumplen con los criterios de la alerta se asocian automáticamente al crear la alerta.
    """
    if 'email' not in session:
        flash("Inicie sesión para crear una alerta")
        return redirect('/')  # Redirigir a login si no hay email en la sesión

    email = session['email']

    # Recuperamos los valores de la sesión
    cpv_search = session.get('cpv_search', '')
    importe1 = session.get('importe1', '')
    fecha1 = session.get('fecha1', None)
    contrato = session.get('contrato', '')
    palabra_clave = session.get('palabra_clave', '')
    importe2 = session.get('importe2', '')
    fecha2 = session.get('fecha2', None)

    # Creamos el string con los valores no vacíos
    alerta_string = "Nueva alerta creada:<br>"
    query = f"""
        SELECT ID FROM (
            (SELECT * FROM licitacion WHERE Fecha_actualización >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH) AND Fecha_de_presentación_de_ofertas IS NULL AND
                Fecha_de_presentación_de_solicitudes_de_participacion IS NULL)
            UNION
            (SELECT * FROM licitacion WHERE (Fecha_de_presentación_de_ofertas IS NOT NULL AND Fecha_de_presentación_de_ofertas >= CURDATE()) OR
                (Fecha_de_presentación_de_solicitudes_de_participacion IS NOT NULL AND Fecha_de_presentación_de_solicitudes_de_participacion >= CURDATE()))
            ) AS subconsulta1
        WHERE Vigente_Anulada_Archivada = 'Vigente' AND (Estado = 'Anuncio previo' OR Estado = 'En plazo')
    """

    if cpv_search:
        alerta_string += f"CPV: {cpv_search};<br>"
        query += f" AND (CPV LIKE '%%{cpv_search}%%' AND CPV REGEXP CONCAT('(^|;)', '{cpv_search}'))"
    if importe1:
        importe1 = importe1.replace(".", "")
        importe1_formateado = f"{int(importe1):,}".replace(",", ".")  # Formatear con puntos
        alerta_string += f"IMPORTE MÍNIMO: {importe1_formateado};<br>"
        query += f" AND Valor_estimado_del_contrato >= '{importe1}'"
    if importe2:
        importe2 = importe2.replace(".", "")
        importe2_formateado = f"{int(importe2):,}".replace(",", ".")  # Formatear con puntos
        alerta_string += f"IMPORTE MÁXIMO {importe2_formateado};<br>"
        query += f" AND Valor_estimado_del_contrato <= '{importe2}'"
    if fecha1:
        fecha1_obj = datetime.strptime(fecha1, "%Y-%m-%d")
        fecha1_sql = fecha1_obj.strftime("%Y-%m-%d")
        alerta_string += f"FECHA MÍNIMA PRESENTACIÓN OFERTAS: {fecha1_sql};<br>"
        query += f" AND Fecha_de_presentación_de_ofertas >= '{fecha1_sql}'"
    if fecha2:
        fecha2_obj = datetime.strptime(fecha2, "%Y-%m-%d")
        fecha2_sql = fecha2_obj.strftime("%Y-%m-%d")
        alerta_string += f"FECHA MÁXIMA PRESENTACIÓN OFERTAS: {fecha2_sql};<br>"
        query += f" AND Fecha_de_presentación_de_ofertas <= '{fecha2_sql}'"
    if contrato:
        alerta_string += f"TIPO DE CONTRATO: {contrato};<br>"
        query += f" AND Tipo_de_contrato = '{contrato}'"
    if palabra_clave:
        alerta_string += f"PALABRA CLAVE: {palabra_clave};<br>"
        query += f"""
                    AND (Objeto_del_Contrato LIKE '%%{palabra_clave}%%' COLLATE utf8mb4_unicode_ci OR
                    Órgano_de_Contratación LIKE '%%{palabra_clave}%%' COLLATE utf8mb4_unicode_ci)
                """
    if len(alerta_string) < 25:
        flash("No se han encontrado datos para crear alerta", "error")
        return redirect('/datos/get_data_lici')

    user_id = db_get_user_id_by_email(email)

    if not user_id:
        return redirect('/datos/get_data_lici')

    # Verificar si el registro ya existe
    result = db_get_alerta_by_all(user_id, cpv_search, contrato, palabra_clave, fecha1, fecha2, importe1, importe2)

    # Insertar solo si no existe
    if not result:
        db_create_alerta_by_all(user_id, cpv_search, contrato, palabra_clave, fecha1, fecha2, importe1, importe2)
        flash("Se ha añadido la alerta correctamente", "success")

        cuerpo = f"""
        <div style="font-family: Arial, sans-serif; text-align: center; margin: 0 20px;">
            <h1 style="font-size: 24px; color: #333;">¡Hola de nuevo, {email}!</h1>
            <p style="font-size: 14px; color: #333;">{alerta_string}</p>
            <p style="font-size: 14px; color: #333;">
                &nbsp;Para manejar las alertas creadas, diríjase a su
                <a href='https://guillermoppm.pythonanywhere.com/'>Perfil</a>.
            </p>
        </div>
        """
        asunto = "Alerta creada"
        mandar_correo(cuerpo, asunto, email)

        id_alerta = db_get_last_alerta_id()

        # Comprobar si hay licitaciones que cumplen la alerta ya insertadas
        with engine.connect() as conn:
            ids_licitaciones = conn.execute(
                text(query)).fetchall()

        for id_lici in ids_licitaciones:
            # Asociar las licitaciones con la alerta para evitar futuras alertas redundantes
            db_create_alerta_licitacion_by_all(id_alerta[0], id_lici[0])

    return redirect('/datos/get_data_lici')





