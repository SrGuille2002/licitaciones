from flask import render_template, request, session, Blueprint
import locale
from utils import limpiar_filtros, agregar_o_actualizar_recomendacion, datos_licitaciones_filtrados, obtener_recomendaciones_principales, datos_consultas_filtrados

datos_bp = Blueprint('dato', __name__)

@datos_bp.route('/get_data_lici', methods=['GET'])
def get_data_lici():
    """
    Maneja la obtención y procesamiento de datos de licitaciones con filtros dinámicos.

    Proceso:
        1. Recupera los parámetros de la solicitud GET, como página, orden, filtros (CPV, palabra clave, importe, fechas, tipo de contrato), y opciones de búsqueda.
        2. Limpia y formatea los valores de los filtros (eliminando puntos en los importes, eliminando espacios innecesarios, etc.).
        3. Si se selecciona la opción 'Buscar', limpia los filtros previos almacenados en la sesión.
        4. Actualiza los valores de los filtros en la sesión y registra recomendaciones personalizadas para el usuario autenticado.
        5. Si no hay una nueva búsqueda, recupera los valores de los filtros almacenados previamente en la sesión.
        6. Llama a una función auxiliar ('datos_licitaciones_filtrados') para obtener los datos filtrados y paginados de las licitaciones.
        7. Formatea los valores de los importes para su visualización (agregando separadores de miles).
        8. Obtiene las recomendaciones principales del usuario autenticado (si existe).
        9. Renderiza la plantilla HTML con los resultados y los parámetros necesarios para la interfaz de usuario.

    Args:
        Ninguno directamente, pero utiliza los parámetros de la solicitud GET.

    Returns:
        Renderiza la plantilla 'index.html' con los siguientes datos:
            - result: Resultados de las licitaciones filtradas y formateadas.
            - page: Número de página actual.
            - total_pages: Número total de páginas.
            - has_results: Indica si hay resultados disponibles.
            - total_results: Número total de resultados.
            - cpv_search: Valor del filtro CPV.
            - importe1: Valor mínimo del filtro de importe.
            - importe2: Valor máximo del filtro de importe.
            - contrato: Tipo de contrato seleccionado.
            - fecha1: Fecha mínima de presentación de ofertas.
            - fecha2: Fecha máxima de presentación de ofertas.
            - palabra_clave: Palabra clave utilizada en la búsqueda.
            - order: Orden de clasificación (ASC o DESC).
            - sort_by: Campo por el que se ordenan los resultados.
            - email: Dirección de correo electrónico del usuario autenticado.
            - recomendaciones_principales: Lista de recomendaciones principales del usuario.
    """
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort_by', None)  # Ordenar por fecha por defecto
    order = request.args.get('order', None)
    cpv_search = request.args.get('cpv_search', '').strip()
    palabra_clave = request.args.get('palabra_clave', '').strip()
    importe1 = request.args.get('importe1', '').strip()
    importe2 = request.args.get('importe2', '').strip()
    fecha1 = request.args.get('fecha1', '').strip()
    fecha2 = request.args.get('fecha2', '').strip()
    contrato = request.args.get('contrato', '').strip()
    boton_buscar = request.args.get('Buscar', None)
    boton_pagina = request.args.get('pagina', None)

    importe1 = importe1.replace(".", "")
    importe2 = importe2.replace(".", "")

    # Limpiar búsquedas previas si se selecciona la opción 'Buscar'
    if boton_buscar:
        limpiar_filtros()

    # Actualizar valores en la sesión
    if order:
        session['order'] = order
    if sort_by:
        session['sort_by'] = sort_by
    if cpv_search:
        session['cpv_search'] = cpv_search
        # Si el usuario está autenticado, actualizar recomendaciones
        if 'email' in session:
            email = session['email']
            agregar_o_actualizar_recomendacion(email, f"CPV: {cpv_search}")
    if palabra_clave:
        session['palabra_clave'] = palabra_clave
        # Si el usuario está autenticado, actualizar recomendaciones
        if 'email' in session:
            email = session['email']
            agregar_o_actualizar_recomendacion(email, f"Palabra clave: {palabra_clave}")
    if importe1:
        session['importe1'] = importe1
    if importe2:
        session['importe2'] = importe2
    if contrato:
        session['contrato'] = contrato
    if fecha1:
        session['fecha1'] = fecha1
    if fecha2:
        session['fecha2'] = fecha2
    if importe1 or importe2:
        # Si el usuario está autenticado, actualizar recomendaciones
        if 'email' in session:
            email = session['email']
            if not importe1:
                importe1 = 0
            if not importe2:
                result = f"Desde {locale.format_string('%d', float(importe1), grouping=True)}€"
            else:
                result = f"Desde {locale.format_string('%d', float(importe1), grouping=True)}€ hasta {locale.format_string('%d', float(importe2), grouping=True)}€"
            agregar_o_actualizar_recomendacion(email, result)

    # Recuperar valores de la sesión si no hay una búsqueda nueva
    if not boton_buscar:
        cpv_search = session.get('cpv_search', '')
        palabra_clave = session.get('palabra_clave', '')
        importe1 = session.get('importe1', '')
        importe2 = session.get('importe2', '')
        fecha1 = session.get('fecha1', '')
        fecha2 = session.get('fecha2', '')
        contrato = session.get('contrato', '')
    if boton_pagina:
        order = session.get('order', None)
        sort_by = session.get('sort_by', None)

    email = session.get('email')
    # Llamar a la función auxiliar con los valores obtenidos de la solicitud
    result, page, total_pages, has_results, total_results = datos_licitaciones_filtrados(
        page=page,
        sort_by=sort_by,
        order=order,
        cpv_search=cpv_search,
        palabra_clave=palabra_clave,
        importe1=importe1,
        importe2=importe2,
        contrato=contrato,
        fecha1=fecha1,
        fecha2=fecha2
    )

    if importe1:
        importe11 = float(importe1)
        importe1 = locale.format_string("%d", importe11, grouping=True)
    if importe2:
        importe22 = float(importe2)
        importe2 = locale.format_string("%d", importe22, grouping=True)

    # Si el usuario está autenticado, se obtienen las tres principales recomendaciones
    recomendaciones_principales = obtener_recomendaciones_principales(email) if email else []

    return render_template(
        'index.html',
        result=result,
        page=page,
        total_pages=total_pages,
        has_results=has_results,
        total_results=total_results,
        cpv_search=cpv_search,
        importe1=importe1,
        importe2=importe2,
        contrato=contrato,
        fecha1=fecha1,
        fecha2=fecha2,
        palabra_clave=palabra_clave,
        order=order,
        sort_by=sort_by,
        email=email,
        recomendaciones_principales=recomendaciones_principales
    )

@datos_bp.route('/get_data_con', methods=['GET'])
def get_data_con():
    """
    Maneja la obtención y procesamiento de datos de consultas preliminares con filtros dinámicos.

    Proceso:
        1. Recupera los parámetros de la solicitud GET, como página, orden, filtros (CPV, palabra clave, fechas, tipo de contrato), y opciones de búsqueda.
        2. Limpia los valores de los filtros eliminando espacios innecesarios.
        3. Si se selecciona la opción 'Buscar', limpia los filtros previos almacenados en la sesión.
        4. Actualiza los valores de los filtros en la sesión para mantener el estado entre solicitudes.
        5. Si no hay una nueva búsqueda, recupera los valores de los filtros almacenados previamente en la sesión.
        6. Llama a una función auxiliar ('datos_consultas_filtrados') para obtener los datos filtrados y paginados de las consultas preliminares.
        7. Renderiza la plantilla HTML con los resultados y los parámetros necesarios para la interfaz de usuario.

    Args:
        Ninguno directamente, pero utiliza los parámetros de la solicitud GET.

    Returns:
        Renderiza la plantilla 'consulta.html' con los siguientes datos:
            - result: Resultados de las consultas preliminares filtradas y formateadas.
            - page: Número de página actual.
            - total_pages: Número total de páginas.
            - has_results: Indica si hay resultados disponibles.
            - total_results: Número total de resultados.
            - cpv_search: Valor del filtro CPV.
            - contrato: Tipo de contrato seleccionado.
            - fecha1: Fecha mínima de presentación de ofertas.
            - fecha2: Fecha máxima de presentación de ofertas.
            - palabra_clave: Palabra clave utilizada en la búsqueda.
            - order: Orden de clasificación (ASC o DESC).
            - sort_by: Campo por el que se ordenan los resultados.
            - email: Dirección de correo electrónico del usuario autenticado.
    """
    page = int(request.args.get('page', 1))
    sort_by = request.args.get('sort_by', None)  # Ordenar por fecha por defecto
    order = request.args.get('order', None)
    cpv_search = request.args.get('cpv_search', '').strip()
    palabra_clave = request.args.get('palabra_clave', '').strip()
    fecha1 = request.args.get('fecha1', '').strip()
    fecha2 = request.args.get('fecha2', '').strip()
    contrato = request.args.get('contrato', '').strip()
    boton_buscar = request.args.get('Buscar', None)
    boton_pagina = request.args.get('pagina', None)

    # Limpiar búsquedas previas si se selecciona la opción 'Buscar'
    if boton_buscar:
        limpiar_filtros()

    # Actualizar valores en la sesión
    if order:
        session['order'] = order
    if sort_by:
        session['sort_by'] = sort_by
    if cpv_search:
        session['cpv_search'] = cpv_search
    if palabra_clave:
        session['palabra_clave'] = palabra_clave
    if contrato:
        session['contrato'] = contrato
    if fecha1:
        session['fecha1'] = fecha1
    if fecha2:
        session['fecha2'] = fecha2

    # Recuperar valores de la sesión si no hay una búsqueda nueva
    if not boton_buscar:
        cpv_search = session.get('cpv_search', '')
        palabra_clave = session.get('palabra_clave', '')
        fecha1 = session.get('fecha1', '')
        fecha2 = session.get('fecha2', '')
        contrato = session.get('contrato', '')
    if boton_pagina:
        order = session.get('order', None)
        sort_by = session.get('sort_by', None)

    email = session.get('email')
    # Llamar a la función auxiliar con los valores obtenidos de la solicitud
    result, page, total_pages, has_results, total_results = datos_consultas_filtrados(
        page=page,
        sort_by=sort_by,
        order=order,
        cpv_search=cpv_search,
        palabra_clave=palabra_clave,
        contrato=contrato,
        fecha1=fecha1,
        fecha2=fecha2
    )

    return render_template(
        'consulta.html',
        result=result,
        page=page,
        total_pages=total_pages,
        has_results=has_results,
        total_results=total_results,
        cpv_search=cpv_search,
        contrato=contrato,
        fecha1=fecha1,
        fecha2=fecha2,
        palabra_clave=palabra_clave,
        order=order,
        sort_by=sort_by,
        email=email,
    )
