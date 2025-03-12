from sqlalchemy import text
from config import engine
import pandas as pd

# Crear DataFrame con los datos del archivo 'subir.xlsx'
print("leyendo excel")
df = pd.read_excel("consulpre.xlsx", sheet_name="Consultas Preliminares")

# Limpiar los datos
df.columns = df.columns.str.replace(' ', '_').str.replace('/', '_')
df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})
print("metiendo datos")

with engine.connect() as connection:
    for _, row in df.iterrows():
        # Para cada fila del DataFrame, definir la consulta SQL para insertar o actualizar registros en la tabla "consulta"
        sql = text("""
        INSERT INTO consulta (
            Identificador, Link_Consulta, Fecha_actualización, Vigente_Anulada_Archivada, Primera_publicación, Estado, Número_de_consulta_preliminar,
            Objeto_de_la_consulta, Fecha_de_inicio_de_la_consulta, Fecha_límite_de_respuesta, Dirección_para_presentación, Tipo_de_consulta,
            Condiciones_o_términos_de_envío_de_la_consulta, Futura_licitación_Tipo_de_contrato, Futura_licitación_Objeto, Futura_licitación_Procedimiento,
            CPV, Órgano_de_Contratación, ID_OC_en_PLACSP, NIF_OC, DIR3, Enlace_al_Perfil_de_Contratante_del_OC, Tipo_de_Administración, Código_Postal
        )
        SELECT :Identificador, :Link_Consulta, :Fecha_actualización, :Vigente_Anulada_Archivada, :Primera_publicación, :Estado, :Número_de_consulta_preliminar,
                :Objeto_de_la_consulta, :Fecha_de_inicio_de_la_consulta, :Fecha_límite_de_respuesta, :Dirección_para_presentación, :Tipo_de_consulta,
                :Condiciones_o_términos_de_envío_de_la_consulta, :Futura_licitación_Tipo_de_contrato, :Futura_licitación_Objeto, :Futura_licitación_Procedimiento,
                :CPV, :Órgano_de_Contratación, :ID_OC_en_PLACSP, :NIF_OC, :DIR3, :Enlace_al_Perfil_de_Contratante_del_OC, :Tipo_de_Administración, :Código_Postal
        ON DUPLICATE KEY UPDATE
            Link_Consulta = VALUES(Link_Consulta),
            Fecha_actualización = VALUES(Fecha_actualización),
            Vigente_Anulada_Archivada = VALUES(Vigente_Anulada_Archivada),
            Primera_publicación = VALUES(Primera_publicación),
            Estado = VALUES(Estado),
            Número_de_consulta_preliminar = VALUES(Número_de_consulta_preliminar),
            Objeto_de_la_consulta = VALUES(Objeto_de_la_consulta),
            Fecha_de_inicio_de_la_consulta = VALUES(Fecha_de_inicio_de_la_consulta),
            Fecha_límite_de_respuesta = VALUES(Fecha_límite_de_respuesta),
            Dirección_para_presentación = VALUES(Dirección_para_presentación),
            Tipo_de_consulta = VALUES(Tipo_de_consulta),
            Condiciones_o_términos_de_envío_de_la_consulta = VALUES(Condiciones_o_términos_de_envío_de_la_consulta),
            Futura_licitación_Tipo_de_contrato = VALUES(Futura_licitación_Tipo_de_contrato),
            Futura_licitación_Objeto = VALUES(Futura_licitación_Objeto),
            Futura_licitación_Procedimiento = VALUES(Futura_licitación_Procedimiento),
            CPV = VALUES(CPV),
            Órgano_de_Contratación = VALUES(Órgano_de_Contratación),
            ID_OC_en_PLACSP = VALUES(ID_OC_en_PLACSP),
            NIF_OC = VALUES(NIF_OC),
            DIR3 = VALUES(DIR3),
            Enlace_al_Perfil_de_Contratante_del_OC = VALUES(Enlace_al_Perfil_de_Contratante_del_OC),
            Tipo_de_Administración = VALUES(Tipo_de_Administración),
            Código_Postal = VALUES(Código_Postal);
        """)

        # Ejecutar la consulta SQL pasando los valores de la fila actual como parámetros
        connection.execute(sql, {
            'Identificador': row.get('Identificador'),
            'Link_Consulta': row.get('Link_Consulta'),
            'Fecha_actualización': row.get('Fecha_actualización'),
            'Vigente_Anulada_Archivada': row.get('Vigente_Anulada_Archivada'),
            'Primera_publicación': row.get('Primera_publicación'),
            'Estado': row.get('Estado'),
            'Número_de_consulta_preliminar': row.get('Número_de_consulta_preliminar'),
            'Objeto_de_la_consulta': row.get('Objeto_de_la_consulta'),
            'Fecha_de_inicio_de_la_consulta': row.get('Fecha_de_inicio_de_la_consulta'),
            'Fecha_límite_de_respuesta': row.get('Fecha_límite_de_respuesta'),
            'Dirección_para_presentación': row.get('Dirección_para_presentación'),
            'Tipo_de_consulta': row.get('Tipo_de_consulta'),
            'Condiciones_o_términos_de_envío_de_la_consulta': row.get('Condiciones_o_términos_de_envío_de_la_consulta'),
            'Futura_licitación_Tipo_de_contrato': row.get('Futura_licitación_Tipo_de_contrato'),
            'Futura_licitación_Objeto': row.get('Futura_licitación_Objeto'),
            'Futura_licitación_Procedimiento': row.get('Futura_licitación_Procedimiento'),
            'CPV': row.get('CPV'),
            'Órgano_de_Contratación': row.get('Órgano_de_Contratación'),
            'ID_OC_en_PLACSP': row.get('ID_OC_en_PLACSP'),
            'NIF_OC': row.get('NIF_OC'),
            'DIR3': row.get('DIR3'),
            'Enlace_al_Perfil_de_Contratante_del_OC': row.get('Enlace_al_Perfil_de_Contratante_del_OC'),
            'Tipo_de_Administración': row.get('Tipo_de_Administración'),
            'Código_Postal': row.get('Código_Postal'),
        })

    print("hecho")

