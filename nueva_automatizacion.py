import xml.etree.ElementTree as ET
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
import zipfile
import sys
import pytz
import pandas as pd
from utils import db_actualizar_licitaciones, db_actualizar_consultas, mandar_alertas

def parse_atom_file(atom_file, entries, tipo):
    """
    Parsea un archivo ATOM y extrae los campos relevantes.
    Args:
        atom_file: Archivo ATOM a procesar.
        processed_ids: Conjunto de IDs ya procesados para evitar duplicados.
        tipo: string que define el tipo de documento (licitación o consulta preliminar)
    Returns:
        Lista de entradas procesadas sin duplicados.
    """
    tree = ET.parse(atom_file)
    root = tree.getroot()
    # Namespace del archivo ATOM
    namespace = {
        'atom': 'http://www.w3.org/2005/Atom',
        'at': 'http://purl.org/atompub/tombstones/1.0',
        'cbc': 'urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2',
        'cac': 'urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2',
        'cbc-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2',
        'cac-place-ext': 'urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2'
    }

    # Mapeo de números a nombres
    contrato_mapeo = {
        "1": "Suministros",
        "2": "Servicios",
        "3": "Obras",
        "21": "Gestión de Servicios Públicos",
        "22": "Concesión de Servicios",
        "31": "Concesión de Obras Públicas",
        "32": "Concesión de Obras",
        "40": "Colaboración entre el sector público y sector privado",
        "7": "Administrativo especial",
        "8": "Privado",
        "50": "Patrimonial"
    }

    estado_mapeo = {
        "PRE": "Anuncio Previo",
        "PUB": "En plazo",
        "EV": "Pendiente de adjudicación",
        "ADJ": "Adjudicada",
        "RES": "Resuelta",
        "ANUL": "Anulada"
    }
    for entry in root.findall('at:deleted-entry', namespace):
        link = entry.attrib.get('ref', '')
        codigo = link.split("/")[-1]  # Extraer el último segmento de la URL

        # Obtener el tipo de comentario (en este caso, siempre será "ANULADA")
        comment_element = entry.find('at:comment', namespace)
        if comment_element is not None:
            comment_type = comment_element.attrib.get('type', '')
            if comment_type == "ANULADA":
                if tipo == "licitaciones":
                    new_entry={
                        "Identificador": codigo,
                        "Link_licitación": None,
                        "Vigente_Anulada_Archivada": comment_type,
                        "Tipo_de_contrato": None,
                        "Órgano_de_Contratación": None,
                        "Valor_estimado_del_contrato": None,
                        "Estado": None,
                        "Objeto_del_Contrato": None,
                        "Fecha_actualización": None,
                        "Presupuesto_base_sin_impuestos": None,
                        "Fecha_de_presentación_de_ofertas": None,
                        "Fecha_de_presentación_de_solicitudes_de_participacion": None,
                        "CPV": None
                    }
                else:
                    new_entry={
                        "Identificador": codigo,
                        "Link_Consulta": None,
                        "Vigente_Anulada_Archivada": comment_type,
                        "Futura_licitación_Tipo_de_contrato": None,
                        "Órgano_de_Contratación": None,
                        "Estado": None,
                        "Objeto_de_la_consulta": None,
                        "Fecha_actualización": None,
                        "Fecha_límite_de_respuesta": None,
                        "CPV": None
                    }
                entries.append(new_entry)

    for entry in root.findall('atom:entry', namespace):

        # Extraer ID
        id_element = entry.find('atom:id', namespace)
        id_value = id_element.text.split("/")[-1] if id_element is not None else None

        # Extraer Link licitación
        link_element = entry.find('atom:link', namespace)
        link_value = link_element.attrib.get('href', '') if link_element is not None else None

        # Extraer Fecha actualización
        updated_element = entry.find('atom:updated', namespace)
        fecha_actualizacion = updated_element.text if updated_element is not None else None

        # Formatear fecha
        fecha_objeto = datetime.fromisoformat(fecha_actualizacion)
        zona_horaria_espana = pytz.timezone("Europe/Madrid")
        fecha_ajustada = fecha_objeto.astimezone(zona_horaria_espana)
        fecha_actualizacion = fecha_ajustada.strftime("%Y-%m-%d %H:%M:%S")

        # Extraer Estado
        if tipo == "licitaciones":
            contract_folder = entry.find('.//cac-place-ext:ContractFolderStatus', namespace)
            contract_folder_status_code = contract_folder.find('cbc-place-ext:ContractFolderStatusCode', namespace)
        else:
            contract_folder = entry.find('.//cac-place-ext:PreliminaryMarketConsultationStatus', namespace)
            contract_folder_status_code = contract_folder.find('cbc-place-ext:PreliminaryMarketConsultationStatusCode', namespace)
        if contract_folder_status_code is not None:
            estado = estado_mapeo.get(contract_folder_status_code.text, None)
        else:
            estado = None

        # Extraer Órgano de contratación
        party_name_element = entry.find(".//cac:Party/cac:PartyName/cbc:Name", namespace)
        organo_contratacion = party_name_element.text if party_name_element is not None else None

        # Extraer Tipo de Contrato
        procurement_projects = entry.find('.//cac:ProcurementProject/cbc:TypeCode', namespace)
        if procurement_projects is not None:
            tipo_contrato = contrato_mapeo.get(procurement_projects.text, "Otros")
        else:
            tipo_contrato = None

        # Extraer Objeto de contrato
        contract_object_element = entry.find(".//cac:ProcurementProject/cbc:Name", namespace)
        objeto_contrato = contract_object_element.text if contract_object_element is not None else None
        if len(objeto_contrato) < 4:
            titulo = entry.find('atom:title', namespace)
            objeto_contrato = titulo.text if titulo is not None else None

        # Extraer CPV
        cpvs = [cpv.text for cpv in entry.findall('.//cac:ProcurementProject/cac:RequiredCommodityClassification/cbc:ItemClassificationCode', namespace)]
        cpv_list = "; ".join(cpvs) if cpvs else None

        if tipo == "licitaciones":
            # Extraer Importe y Presupuesto
            procurement_project = entry.find('.//cac:ProcurementProject', namespace)
            budget_amount = procurement_project.find('.//cac:BudgetAmount', namespace)
            if budget_amount is not None:
                import_amount = budget_amount.find('cbc:EstimatedOverallContractAmount', namespace)
                importe = import_amount.text if import_amount is not None else None
                estimated_amount = budget_amount.find('cbc:TaxExclusiveAmount', namespace)
                presupuesto = estimated_amount.text if estimated_amount is not None else None
            else:
                importe = None
                presupuesto = None

            # Extraer Fecha de presentación de oferta
            tendering_process = entry.find('.//cac:TenderingProcess', namespace)
            tender_period = tendering_process.find('.//cac:TenderSubmissionDeadlinePeriod', namespace)
            if tender_period is not None:
                end_date = tender_period.find('cbc:EndDate', namespace)
                end_time = tender_period.find('cbc:EndTime', namespace)
                if end_date is None or end_time is None:
                    fecha_oferta = None
                else:
                    fecha_oferta = f"{end_date.text} {end_time.text}".strip()
            else:
                fecha_oferta = None

            # Extraer Fecha de solicitudes de participación
            tendering_process = entry.find('.//cac:TenderingProcess', namespace)
            availability_period = tendering_process.find('.//cac:ParticipationRequestReceptionPeriod', namespace)
            if availability_period is not None:
                end_date = availability_period.find('cbc:EndDate', namespace)
                end_time = availability_period.find('cbc:EndTime', namespace)
                if end_date is None or end_time is None:
                    fecha_solicitudes = None
                else:
                    fecha_solicitudes = f"{end_date.text} {end_time.text}".strip()
            else:
                fecha_solicitudes = None

        else: # "consultas"
            # Extraer Fecha limite
            fecha_limite_code = entry.find('.//cac-place-ext:PreliminaryMarketConsultationStatus/cbc:LimitDate', namespace)
            if fecha_limite_code is not None:
                fecha_limite = fecha_limite_code.text if fecha_limite_code is not None else None
            else:
                fecha_limite = None

        # Crear un diccionario con los datos de la entrada
        if tipo == "licitaciones":
            new_entry={
                "Identificador": id_value,
                "Link_licitación": link_value,
                "Vigente_Anulada_Archivada": "Vigente",
                "Tipo_de_contrato": tipo_contrato,
                "Órgano_de_Contratación": organo_contratacion,
                "Valor_estimado_del_contrato": importe,
                "Estado": estado,
                "Objeto_del_Contrato": objeto_contrato,
                "Fecha_actualización": fecha_actualizacion,
                "Presupuesto_base_sin_impuestos": presupuesto,
                "Fecha_de_presentación_de_ofertas": fecha_oferta,
                "Fecha_de_presentación_de_solicitudes_de_participacion": fecha_solicitudes,
                "CPV": cpv_list
            }
        else:
            new_entry={
                "Identificador": id_value,
                "Link_Consulta": link_value,
                "Vigente_Anulada_Archivada": "Vigente",
                "Futura_licitación_Tipo_de_contrato": tipo_contrato,
                "Órgano_de_Contratación": organo_contratacion,
                "Estado": estado,
                "Objeto_de_la_consulta": objeto_contrato,
                "Fecha_actualización": fecha_actualizacion,
                "Fecha_límite_de_respuesta": fecha_limite,
                "CPV": cpv_list
            }
        entries.append(new_entry)

    return entries

def descarga_y_procesamiento(link):
    print("Descargando archivo ...")
    print("Link de descarga: " + link)
    response = requests.get(link, headers=headers)

    # Verificamos si la descarga fue exitosa
    if response.status_code == 200:
        # Guardamos el archivo en el sistema
        with open("fichero_raiz.zip", "wb") as file:
            file.write(response.content)
        print("Descarga completada.")
    else:
        print(f"Error al descargar el archivo: {response.status_code}")
        sys.exit("Descarga no exitosa")

    ruta_zip = "fichero_raiz.zip"
    entries = []

    print("Procesando archivos ...")
    with zipfile.ZipFile(ruta_zip, 'r') as zip_ref:
        # Obtener la lista de archivos en el ZIP
        files = zip_ref.namelist()
        if files[0].startswith("CPM"):
            for file in files:
                with zip_ref.open(file) as atom_file:
                    entries = parse_atom_file(atom_file, entries, "consulta")
        else:
            # Procesar cada archivo en el orden correcto
            for file in files:
                with zip_ref.open(file) as atom_file:
                    entries = parse_atom_file(atom_file, entries, "licitaciones")

    print("Creando dataframe ...")
    df = pd.DataFrame(entries)
    df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})
    df = df.drop_duplicates(subset=["Identificador"], keep="last")
    print("Dataframe creado")
    return df


url = "https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3_"
url2 = "https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_1044/PlataformasAgregadasSinMenores_"
url3 = "https://contrataciondelsectorpublico.gob.es/sindicacion/sindicacion_1403/CPM_SectorPublico_"

# Configuración: Rutas y variables
hoy = datetime.now()
# Verificar si el día actual es 1
if hoy.day == 1:
    # Restar un mes a la fecha actual
    fecha_ajustada = hoy - relativedelta(months=1)
else:
    # Usar la fecha actual si el día no es 1
    fecha_ajustada = hoy

# Extraer el año y el mes ajustados
año_actual = fecha_ajustada.year
mes_actual = fecha_ajustada.strftime("%m")  # '01', '02', etc.

patron_busqueda = f"{año_actual}{mes_actual}"  # Formato: 202311 (año + mes)
link = f"{url}{patron_busqueda}.zip"
link2 = f"{url2}{patron_busqueda}.zip"
link3 = f"{url3}{año_actual}.zip"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "application/zip",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

print("Descarga y procesamiento de licitaciones normales")
df_licitaciones = descarga_y_procesamiento(link)
print("Descarga y procesamiento de licitaciones insertadas por mecanismos de agregación")
df_licitaciones2 = descarga_y_procesamiento(link2)
print("Descarga y procesamiento de consultas preliminares")
df_consultas = descarga_y_procesamiento(link3)

# Concatenar los DataFrames y eliminar filas duplicadas
df_licitaciones = pd.concat([df_licitaciones, df_licitaciones2], ignore_index=True)
df_licitaciones = df_licitaciones.drop_duplicates()

# Actualizando base de datos de licitaciones
db_actualizar_licitaciones(df_licitaciones)
# Mandar las alertas a los usuarios
print("Mandando alertas de licitaciones")
mandar_alertas()

# Actualizando base de datos de consultas
db_actualizar_consultas(df_consultas)