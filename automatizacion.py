from sqlalchemy import text
import pandas as pd
from config import engine
from utils import mandar_alertas

# Crear DataFrame con los datos del archivo 'subir.xlsx'
print("leyendo excel")
df = pd.read_excel("archivo_salida_2.xlsx", sheet_name="Licitaciones")

# Limpiar los datos
df.columns = df.columns.str.replace(' ', '_').str.replace('/', '_')
df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})
print("metiendo datos")

with engine.connect() as connection:
    for _, row in df.iterrows():
        # Para cada fila del DataFrame, definir la consulta SQL para insertar o actualizar registros en la tabla "licitacion"
        sql = text("""
        INSERT INTO licitacion (
            Identificador, Link_licitación, Fecha_actualización, Vigente_Anulada_Archivada,
            Primera_publicación, Estado, Número_de_expediente, Objeto_del_Contrato,
            Valor_estimado_del_contrato, Presupuesto_base_sin_impuestos, Presupuesto_base_con_impuestos,
            CPV, Tipo_de_contrato, Lugar_de_ejecución, Órgano_de_Contratación, ID_OC_en_PLACSP,
            NIF_OC, DIR3, Enlace_al_Perfil_de_Contratante_del_OC, Tipo_de_Administración,
            Código_Postal, Tipo_de_procedimiento, Sistema_de_contratación, Tramitación,
            Forma_de_presentación_de_la_oferta, Fecha_de_presentación_de_ofertas,
            Fecha_de_presentación_de_solicitudes_de_participacion, Directiva_de_aplicación,
            Financiación_Europea_y_fuente, Descripción_de_la_financiación_europea,
            Subcontratación_permitida, Subcontratación_permitida_porcentaje
        )
        SELECT :Identificador, :Link_licitación, :Fecha_actualización, :Vigente_Anulada_Archivada,
               :Primera_publicación, :Estado, :Número_de_expediente, :Objeto_del_Contrato,
               :Valor_estimado_del_contrato, :Presupuesto_base_sin_impuestos, :Presupuesto_base_con_impuestos,
               :CPV, :Tipo_de_contrato, :Lugar_de_ejecución, :Órgano_de_Contratación, :ID_OC_en_PLACSP,
               :NIF_OC, :DIR3, :Enlace_al_Perfil_de_Contratante_del_OC, :Tipo_de_Administración,
               :Código_Postal, :Tipo_de_procedimiento, :Sistema_de_contratación, :Tramitación,
               :Forma_de_presentación_de_la_oferta, :Fecha_de_presentación_de_ofertas,
               :Fecha_de_presentación_de_solicitudes_de_participacion, :Directiva_de_aplicación,
               :Financiación_Europea_y_fuente, :Descripción_de_la_financiación_europea,
               :Subcontratación_permitida, :Subcontratación_permitida_porcentaje
        ON DUPLICATE KEY UPDATE
            Link_licitación = VALUES(Link_licitación),
            Fecha_actualización = VALUES(Fecha_actualización),
            Vigente_Anulada_Archivada = VALUES(Vigente_Anulada_Archivada),
            Primera_publicación = VALUES(Primera_publicación),
            Estado = VALUES(Estado),
            Número_de_expediente = VALUES(Número_de_expediente),
            Objeto_del_Contrato = VALUES(Objeto_del_Contrato),
            Valor_estimado_del_contrato = VALUES(Valor_estimado_del_contrato),
            Presupuesto_base_sin_impuestos = VALUES(Presupuesto_base_sin_impuestos),
            Presupuesto_base_con_impuestos = VALUES(Presupuesto_base_con_impuestos),
            CPV = VALUES(CPV),
            Tipo_de_contrato = VALUES(Tipo_de_contrato),
            Lugar_de_ejecución = VALUES(Lugar_de_ejecución),
            Órgano_de_Contratación = VALUES(Órgano_de_Contratación),
            ID_OC_en_PLACSP = VALUES(ID_OC_en_PLACSP),
            NIF_OC = VALUES(NIF_OC),
            DIR3 = VALUES(DIR3),
            Enlace_al_Perfil_de_Contratante_del_OC = VALUES(Enlace_al_Perfil_de_Contratante_del_OC),
            Tipo_de_Administración = VALUES(Tipo_de_Administración),
            Código_Postal = VALUES(Código_Postal),
            Tipo_de_procedimiento = VALUES(Tipo_de_procedimiento),
            Sistema_de_contratación = VALUES(Sistema_de_contratación),
            Tramitación = VALUES(Tramitación),
            Forma_de_presentación_de_la_oferta = VALUES(Forma_de_presentación_de_la_oferta),
            Fecha_de_presentación_de_ofertas = VALUES(Fecha_de_presentación_de_ofertas),
            Fecha_de_presentación_de_solicitudes_de_participacion = VALUES(Fecha_de_presentación_de_solicitudes_de_participacion),
            Directiva_de_aplicación = VALUES(Directiva_de_aplicación),
            Financiación_Europea_y_fuente = VALUES(Financiación_Europea_y_fuente),
            Descripción_de_la_financiación_europea = VALUES(Descripción_de_la_financiación_europea),
            Subcontratación_permitida = VALUES(Subcontratación_permitida),
            Subcontratación_permitida_porcentaje = VALUES(Subcontratación_permitida_porcentaje);
        """)

        # Ejecutar la consulta SQL pasando los valores de la fila actual como parámetros
        connection.execute(sql, {
            'Identificador': row.get('Identificador'),
            'Link_licitación': row.get('Link_licitación'),
            'Fecha_actualización': row.get('Fecha_actualización'),
            'Vigente_Anulada_Archivada': row.get('Vigente_Anulada_Archivada'),
            'Primera_publicación': row.get('Primera_publicación'),
            'Estado': row.get('Estado'),
            'Número_de_expediente': row.get('Número_de_expediente'),
            'Objeto_del_Contrato': row.get('Objeto_del_Contrato'),
            'Valor_estimado_del_contrato': row.get('Valor_estimado_del_contrato'),
            'Presupuesto_base_sin_impuestos': row.get('Presupuesto_base_sin_impuestos'),
            'Presupuesto_base_con_impuestos': row.get('Presupuesto_base_con_impuestos'),
            'CPV': row.get('CPV'),
            'Tipo_de_contrato': row.get('Tipo_de_contrato'),
            'Lugar_de_ejecución': row.get('Lugar_de_ejecución'),
            'Órgano_de_Contratación': row.get('Órgano_de_Contratación'),
            'ID_OC_en_PLACSP': row.get('ID_OC_en_PLACSP'),
            'NIF_OC': row.get('NIF_OC'),
            'DIR3': row.get('DIR3'),
            'Enlace_al_Perfil_de_Contratante_del_OC': row.get('Enlace_al_Perfil_de_Contratante_del_OC'),
            'Tipo_de_Administración': row.get('Tipo_de_Administración'),
            'Código_Postal': row.get('Código_Postal'),
            'Tipo_de_procedimiento': row.get('Tipo_de_procedimiento'),
            'Sistema_de_contratación': row.get('Sistema_de_contratación'),
            'Tramitación': row.get('Tramitación'),  # Si no existe, será None
            'Forma_de_presentación_de_la_oferta': row.get('Forma_de_presentación_de_la_oferta'),
            'Fecha_de_presentación_de_ofertas': row.get('Fecha_de_presentación_de_ofertas'),
            'Fecha_de_presentación_de_solicitudes_de_participacion': row.get('Fecha_de_presentación_de_solicitudes_de_participacion'),
            'Directiva_de_aplicación': row.get('Directiva_de_aplicación'),
            'Financiación_Europea_y_fuente': row.get('Financiación_Europea_y_fuente'),
            'Descripción_de_la_financiación_europea': row.get('Descripción_de_la_financiación_europea'),
            'Subcontratación_permitida': row.get('Subcontratación_permitida'),
            'Subcontratación_permitida_porcentaje': row.get('Subcontratación_permitida_porcentaje'),
        })

    print("hecho")

# Mandar las alertas a los usuarios
#mandar_alertas()
