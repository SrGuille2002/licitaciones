import pandas as pd
import locale
from .consultasbd_utils import db_get_datos, db_get_cpvs
from .miscelanea_utils import procesar_datos_html

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

# Función auxiliar para obtener los datos iniciales con paginación y filtrado
def datos_licitaciones_filtrados(page=1, limit=10, sort_by='Fecha_actualización', order='ASC', cpv_search=None, palabra_clave=None, importe1=None, importe2=None, contrato=None, fecha1=None, fecha2=None):
    """
    Obtiene datos filtrados de la tabla licitacion con paginación y formato HTML.

    Args:
        page (int): Número de página actual.
        limit (int): Número de resultados por página.
        sort_by (str): Columna por la que se ordenan los resultados.
        order (str): Dirección del ordenamiento ('ASC' o 'DESC').
        cpv_search (str): Filtro por código CPV.
        palabra_clave (str): Filtro por palabra clave en el objeto del contrato u órgano de contratación.
        importe1 (int): Filtro por importe mínimo.
        importe2 (int): Filtro por importe máximo.
        contrato (str): Filtro por tipo de contrato.
        fecha1 (str): Filtro por fecha mínima de presentación de ofertas.
        fecha2 (str): Filtro por fecha máxima de presentación de ofertas.

    Returns:
        tuple: Contiene los siguientes elementos:
            - result (str): HTML con los resultados formateados.
            - page (int): Número de página actual.
            - total_pages (int): Número total de páginas.
            - has_results (bool): Indica si hay resultados disponibles.
            - total_results (int): Número total de resultados encontrados.
    """
    tabla = 'licitacion'

    # Acceder a la base de datos y extraer los datos requeridos
    df = db_get_datos(tabla, page, limit, sort_by, order, cpv_search, palabra_clave, contrato, fecha1, fecha2, importe1, importe2)
    if len(df) == 0: # Dataframe vacío
        total_pages = 0
        total_results = 0
    else: # Registros para las páginas
        total_results = df['total_count'].iloc[0]
        total_pages = (total_results // limit)
        if total_results % limit > 0:
            total_pages += 1

    # Reemplazar valores nulos por None para evitar errores en el renderizado
    df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})
    df = df.replace({pd.NaT: None})
    df = df.replace({float('nan'): None})
    df['Fecha_de_presentación_de_ofertas'] = df['Fecha_de_presentación_de_ofertas'].fillna("No disponible")
    df['Fecha_de_presentación_de_solicitudes_de_participacion'] = df['Fecha_de_presentación_de_solicitudes_de_participacion'].fillna("No disponible")

    # Aplicar el formato con decimales para las columnas del dataframe
    df['Valor_estimado_del_contrato'] = df['Valor_estimado_del_contrato'].apply(
        lambda x: locale.format_string("%.2f", x, grouping=True) if x is not None else 'No disponible')
    df['Presupuesto_base_sin_impuestos'] = df['Presupuesto_base_sin_impuestos'].apply(
        lambda x: locale.format_string("%.2f", x, grouping=True) if x is not None else 'No disponible')

    # Mapear nombres de CPVs
    cpv_df = db_get_cpvs()
    cpv_map = dict(zip(cpv_df['numero'], cpv_df['nombre']))

    # Preparar el HTML con los resultados
    MAX_CHARACTERS = 150
    result_list = []
    for index, row in df.iterrows():
        objeto_contrato, cpv_content, document_link, fecha_ofe_html, fecha_sol_html, importe_html = procesar_datos_html("licitaciones", row, cpv_map, MAX_CHARACTERS)

        result_list.append(
            f"<strong>Título del Contrato:</strong> <span class='contract-object'>{objeto_contrato}</span><br>"
            f"<strong>Actualizado a:</strong> {row['Fecha_actualización'] or 'No disponible'}<br>"
            f"<strong>Tipo de contrato:</strong> {row['Tipo_de_contrato'] or 'No disponible'}<br>"
            f"<strong>Órgano de Contratación:</strong> {row['Órgano_de_Contratación'] or 'No disponible'}<br>"
            f"<strong>CPVs:</strong> {cpv_content}<br>"  # Incluir CPVs con hover
            f"<strong>Fecha fin de presentación de ofertas:</strong> {fecha_ofe_html}<br>"
            f"<strong>Fecha límite de solicitud:</strong> {fecha_sol_html}<br>"
            f"<div class='row-container'>"
            f"  <div class='left-content'><strong>Importe:</strong> {importe_html}</div>"
            f"  {document_link}"
            f"</div>"
            "<hr>"  # Cerrar el div
        )

    result = "".join(result_list)

    # Retornar resultados y valores de paginación
    return result, page, total_pages, not df.empty, total_results

def datos_consultas_filtrados(page=1, limit=10, sort_by='Fecha_actualización', order='ASC', cpv_search=None, palabra_clave=None, contrato=None, fecha1=None, fecha2=None):
    """
    Obtiene datos de consultas preliminares filtrados y paginados para su visualización.

    Args:
        page (int): Número de página actual (por defecto 1).
        limit (int): Número máximo de resultados por página (por defecto 10).
        sort_by (str): Campo por el que se ordenan los resultados (por defecto 'Fecha_actualización').
        order (str): Orden de los resultados ('ASC' o 'DESC', por defecto 'ASC').
        cpv_search (str): Código CPV para filtrar resultados (opcional).
        palabra_clave (str): Palabra clave para buscar en campos específicos (opcional).
        contrato (str): Tipo de contrato para filtrar resultados (opcional).
        fecha1 (str): Fecha mínima para filtrar por límite de respuesta (formato YYYY-MM-DD, opcional).
        fecha2 (str): Fecha máxima para filtrar por límite de respuesta (formato YYYY-MM-DD, opcional).

    Returns:
        tuple: Contiene los siguientes elementos:
            - result (str): HTML con los resultados formateados.
            - page (int): Número de página actual.
            - total_pages (int): Número total de páginas.
            - has_results (bool): Indica si hay resultados disponibles.
            - total_results (int): Número total de resultados encontrados.
    """
    tabla = 'consulta'

    # Acceder a la base de datos y extraer los datos requeridos
    df = db_get_datos(tabla, page, limit, sort_by, order, cpv_search, palabra_clave, contrato, fecha1, fecha2)
    if len(df) == 0: # Dataframe vacío
        total_pages = 0
        total_results = 0
    else: # Registros para las páginas
        total_results = df['total_count'].iloc[0]
        total_pages = (total_results // limit)
        if total_results % limit > 0:
            total_pages += 1

    # Limpiar valores nulos en el DataFrame para evitar errores en el renderizado
    df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})
    df = df.replace({pd.NaT: None})
    df = df.replace({float('nan'): None})

    # Obtener un mapeo de códigos CPV a nombres descriptivos
    cpv_df = db_get_cpvs()
    cpv_map = dict(zip(cpv_df['numero'], cpv_df['nombre']))

    # Preparar el HTML con los resultados
    MAX_CHARACTERS = 150  # Máximo de caracteres para recortar el título del contrato
    result_list = []
    for index, row in df.iterrows():
        objeto_contrato, cpv_content, document_link, fecha_res_html = procesar_datos_html("consultas", row, cpv_map, MAX_CHARACTERS)

        # Formatear cada resultado como HTML
        result_list.append(
            f"<strong>Título del Contrato:</strong> <span class='contract-object'>{objeto_contrato}</span><br>"
            f"<strong>Actualizado a:</strong> {row['Fecha_actualización'] or 'No disponible'}<br>"
            f"<strong>Tipo de contrato:</strong> {row['Futura_licitación_Tipo_de_contrato'] or 'No disponible'}<br>"
            f"<strong>Órgano de Contratación:</strong> {row['Órgano_de_Contratación'] or 'No disponible'}<br>"
            f"<strong>CPVs:</strong> {cpv_content}<br>"
            f"<div class='row-container'>"
            f"  <div class='left-content'><strong>Fecha límite de respuesta:</strong> {fecha_res_html}</div>"
            f"  {document_link}"
            f"</div>"
            "<hr>"  # Separador entre resultados
        )

    # Unir todos los resultados en una cadena HTML
    result = "".join(result_list)

    # Retornar los resultados y la información de paginación
    return result, page, total_pages, not df.empty, total_results