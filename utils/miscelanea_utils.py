from flask import session, Flask, url_for
from flask_mail import Mail, Message
from config import SECRET_KEY, MAIL_CONFIG

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configuración de Flask-Mail
app.config.update(MAIL_CONFIG)
mail = Mail(app)

def format_importe(importe):
    """
    Formatea un valor numérico como importe con separadores de miles.

    Args:
        importe (int o float): El valor numérico a formatear.
                               Si es None, se retorna None.

    Returns:
        str: El importe formateado con puntos como separadores de miles.
             Si el importe es None, retorna None.
    """
    # Verifica si el valor de 'importe' no es None
    if importe:
        # Convierte el importe a entero (en caso de que sea float) y lo formatea
        # con comas como separadores de miles, luego reemplaza las comas por puntos
        return f"{int(importe):,}".replace(",", ".")
    else:
        # Si el importe es None, retorna None
        return None

def limpiar_filtros():
    """
    Limpia todas las variables de sesión relacionadas con los filtros de búsqueda.

    Esta función elimina las siguientes claves de la sesión si existen:
    - 'cpv_search': Filtro por código CPV.
    - 'palabra_clave': Filtro por palabra clave en el objeto del contrato u órgano de contratación.
    - 'importe1': Filtro por importe mínimo.
    - 'importe2': Filtro por importe máximo.
    - 'fecha1': Filtro por fecha mínima de presentación de ofertas.
    - 'fecha2': Filtro por fecha máxima de presentación de ofertas.
    - 'contrato': Filtro por tipo de contrato.
    - 'order': Orden de los resultados (ASC o DESC).
    - 'sort_by': Columna por la que se ordenan los resultados.

    Si alguna de estas claves no existe en la sesión, 'session.pop()' simplemente no hará nada para esa clave.
    """
    session.pop('cpv_search', None)
    session.pop('palabra_clave', None)
    session.pop('importe1', None)
    session.pop('importe2', None)
    session.pop('fecha1', None)
    session.pop('fecha2', None)
    session.pop('contrato', None)
    session.pop('order', None)
    session.pop('sort_by', None)

def mandar_correo(cuerpo, asunto, email):
    """
    Envía un correo electrónico a un destinatario específico.

    Args:
        cuerpo (str): El contenido del mensaje que se enviará en el correo.
        asunto (str): El asunto del correo.
        email (str): La dirección de correo electrónico del destinatario.

    Returns:
        None: La función no retorna ningún valor explícito, pero imprime un mensaje
              indicando si el correo fue enviado o si ocurrió un error.
    """
    try:
        # Asegurarse de que el código se ejecute dentro del contexto de la aplicación
        with app.app_context():
            # Crear un objeto Message con el asunto, destinatario y remitente
            msg = Message(
                subject=asunto,
                recipients=[email],
                sender=app.config['MAIL_DEFAULT_SENDER']  # Remitente desde la configuración
            )
            msg.html = cuerpo

            # Enviar el correo
            mail.send(msg)
            print(f"Correo enviado a {email}")
    except Exception as e:
        # Capturar y mostrar cualquier error que ocurra durante el envío
        print(f"Error al enviar el correo: {str(e)}")

def procesar_datos_html(tipo_dato, row, cpvs_con_nombre, MAX_CHARACTERS):
    """
    Procesa los datos de una fila específica para ser representados en formato HTML.

    Args:
        tipo_dato (str): Indica si el tipo de dato es 'licitaciones' o 'consulta'.
                         Determina cómo se procesan ciertos campos.
        row (dict): Diccionario que contiene los datos de una fila específica.
        cpvs_con_nombre (dict): Diccionario que mapea códigos CPV a sus nombres correspondientes.
        MAX_CHARACTERS (int): Límite máximo de caracteres para recortar campos largos.

    Returns:
        tuple: Dependiendo del tipo de dato, retorna una tupla con los siguientes elementos:
            - Para 'licitaciones':
                - objeto_contrato (str): Objeto del contrato procesado.
                - cpv_content (str): Contenido HTML formateado para los CPVs.
                - document_link (str): Enlace HTML al documento o mensaje de inicio de sesión.
                - fecha_ofe_html (str): Fecha de presentación de ofertas procesada.
                - fecha_sol_html (str): Fecha de solicitud de participación procesada.
                - importe_html (str): Valor estimado del contrato procesado.
            - Para otros tipos:
                - objeto_contrato (str): Objeto de la consulta procesado.
                - cpv_content (str): Contenido HTML formateado para los CPVs.
                - document_link (str): Enlace HTML al documento o mensaje de inicio de sesión.
                - fecha_ofe_html (str): Fecha límite de respuesta procesada.
    """
    if tipo_dato == "licitaciones":
        objeto_contrato = row['Objeto_del_Contrato'] or 'No disponible'
    else:
        objeto_contrato = row['Objeto_de_la_consulta'] or 'No disponible'
    if len(objeto_contrato) > MAX_CHARACTERS:
        objeto_contrato = objeto_contrato[:MAX_CHARACTERS] + "[...]"  # Recortar y añadir "..."

    # Procesar CPVs
    if row['CPV']:
        cpvs_licitacion = row['CPV'].split(';')
        # Procesar el primer CPV
        primer_cpv = cpvs_licitacion[0].strip()
        primer_cpv_nombre = cpvs_con_nombre.get(primer_cpv, "Nombre desconocido")
        cpv_display = f"{primer_cpv} - {primer_cpv_nombre}"  # Formato: Numerocpv - nombrecpv

        if len(cpvs_licitacion) > 2:
            # Procesar los CPVs restantes para el hover
            cpv_display += ", ..."
            cpvs_restantes = cpvs_licitacion[1:]
            cpvs_hover = []
            for cpv in cpvs_restantes:
                cpv_nombre = cpvs_con_nombre.get(cpv.strip(), "-")
                if cpv_nombre != "-": # Si el cpv existe y tiene nombre
                    # Añadir a la lista el siguiente cpv con su nombre
                    cpvs_hover.append(f"{cpv.strip()} - {cpv_nombre}")
            cpvs_hover_content = " ".join(cpvs_hover) if cpvs_hover else "No hay más CPVs"

            # Construir el HTML final
            cpv_content = (
                f"<span class='highlight-cpv' title='{cpvs_hover_content}'>"
                f"{cpv_display}</span>"
            )
        else:
            cpv_content = f"<span style='font-style: italic; color: #ff7300;'>{cpv_display}</span>"
    else:
        # Si no hay CPVs, mostrar "No disponible"
        cpv_content = f"<span style='color: red;'>No disponible</span>"

    # Verificar si el usuario está autenticado
    if 'email' in session:
        # Si está autenticado, mostrar el enlace
        if tipo_dato == "licitaciones":
            document_link = f"<a href='{row['Link_licitación'] or '#'}' target='_blank' style='font-size: 3em;' class='document-link'>Documentos</a>"
        else:
            document_link = f"<a href='{row['Link_Consulta'] or '#'}' target='_blank' style='font-size: 2.5em;' class='document-link'>Documentos</a>"
    else:
        # Si no está autenticado, mostrar el mensaje
        login_url = url_for('login_register')  # Genera la URL para el inicio de sesión
        document_link = (
            f"<a href='{login_url}' class='document-link' style='font-size: 2em;'>"
            "Inicia sesión para más información."
            "</a>"
        )

    # Procesar valores de fecha Nulos
    if tipo_dato == "licitaciones":
        fecha_ofe = row['Fecha_de_presentación_de_ofertas']
    else:
        fecha_ofe = row['Fecha_límite_de_respuesta']
    if not fecha_ofe or fecha_ofe == '0000-00-00 00:00:00':
        fecha_ofe = 'No disponible'
        fecha_ofe_html = f"<span style='color: red;'>{fecha_ofe}</span>"
    else:
        fecha_ofe_html = fecha_ofe

    if tipo_dato == "licitaciones": # Campos adicionales de los datos "licitaciones"
        fecha_sol = row['Fecha_de_presentación_de_solicitudes_de_participacion']
        if not fecha_sol or fecha_sol == '0000-00-00 00:00:00':
            fecha_sol = 'No disponible'
            fecha_sol_html = f"<span style='color: red;'>{fecha_sol}</span>"
        else:
            fecha_sol_html = fecha_sol

        # Procesar valores de importes Nulos
        importe = row['Valor_estimado_del_contrato']
        if importe == "No disponible":
            importe_html = f"<span style='color: red;'>{importe}</span>"
        else:
            importe_html = importe + " €"

        return objeto_contrato, cpv_content, document_link, fecha_ofe_html, fecha_sol_html, importe_html
    else: # tipo de dato "consulta"
        return objeto_contrato, cpv_content, document_link, fecha_ofe_html


