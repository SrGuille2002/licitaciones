import unittest
from unittest.mock import patch
from sqlalchemy import text
from flask_app import app
from config import engine
from utils import db_get_user_id_by_email, db_get_user_by_email, db_create_user_by_all, datos_licitaciones_filtrados, db_get_top3_recomendaciones_by_user_id, db_create_alerta_by_all, get_alertas

class TestAppFunctions(unittest.TestCase):
    """
    Clase para realizar pruebas unitarias de las funciones del sistema.
    """

    def setUp(self):
        """
        Configuración inicial antes de cada prueba.
        """
        self.app = app.test_client()  # Cliente de prueba para simular solicitudes HTTP
        self.app.testing = True  # Habilita el modo de pruebas
        self.email = "test@example.com"
        self.password = "securepassword123"
        self.cpv_search = "44511"
        self.contrato = "Servicios"
        self.palabra_clave = "prueba"
        self.importe1 = "1000"
        self.importe2 = "5000"
        self.fecha1 = "2025-10-01"
        self.fecha2 = "2025-10-31"

        # Limpiar la base de datos antes de cada prueba
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM usuarios WHERE email = :email"), {"email": self.email})

    def tearDown(self):
        """
        Limpieza después de cada prueba.
        """
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM usuarios WHERE email = :email"), {"email": self.email})

    ### PRUEBAS UNITARIAS

    def test_db_get_user_by_email(self):
        """
        Prueba la función db_get_user_by_email.
        """
        # Crear un usuario de prueba
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO usuarios (email, password) VALUES (:email, :password)"),
                {"email": self.email, "password": self.password}
            )

        # Obtener el usuario
        user = db_get_user_by_email(self.email)
        self.assertIsNotNone(user, "El usuario no debería ser None")
        self.assertEqual(user["email"], self.email, "El correo electrónico no coincide")

    def test_db_create_user_by_all(self):
        """
        Prueba la función db_create_user_by_all.
        """
        # Crear un usuario de prueba
        db_create_user_by_all(self.email, self.password)

        # Verificar que el usuario fue creado
        with engine.connect() as conn:
            user = conn.execute(
                text("SELECT * FROM usuarios WHERE email = :email"),
                {"email": self.email}
            ).fetchone()
        self.assertIsNotNone(user, "El usuario no debería ser None")
        self.assertEqual(user["email"], self.email, "El correo electrónico no coincide")

    def test_obtener_datos_iniciales(self):
        """
        Prueba la función datos_licitaciones_filtrados.
        """
        # Insertar datos de prueba en la tabla 'licitacion'
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO licitacion (CPV, Vigente_Anulada_Archivada, Estado, Tipo_de_contrato, Objeto_del_Contrato, Valor_estimado_del_contrato, Fecha_de_presentación_de_ofertas)
                    VALUES (:cpv, :vigencia, :estado, :contrato, :objeto, :importe, :fecha_limite)
                """),
                {
                    "cpv": self.cpv_search,
                    "vigencia": "Vigente",
                    "estado": "En plazo",
                    "contrato": self.contrato,
                    "objeto": "Licitación de prueba",
                    "importe": 3000,
                    "fecha_limite": "2025-10-02"
                }
            )

        # Simular un contexto de solicitud completo
        with app.test_request_context():

            # Simular datos en la sesión
            with self.app.session_transaction() as session:
                session['email'] = self.email

            # Obtener datos iniciales
            result, page, total_pages, has_results, total_results = datos_licitaciones_filtrados(
                cpv_search=self.cpv_search,
                contrato=self.contrato,
                palabra_clave=self.palabra_clave,
                importe1=self.importe1,
                importe2=self.importe2,
                fecha1=self.fecha1,
                fecha2=self.fecha2
            )

            # Verificar resultados
            self.assertTrue(has_results, "Se esperaban resultados")
            self.assertGreater(total_results, 0, "El número total de resultados debería ser mayor que 0")

            # Eliminación de licitación
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM licitacion WHERE cpv = :cpv and Objeto_del_Contrato = :objeto"), {"cpv": self.cpv_search, "objeto": "Licitacion de prueba"})

    def test_db_create_alerta_by_all(self):
        """
        Prueba la función db_create_alerta_by_all.
        """
        # Crear un usuario de prueba
        db_create_user_by_all(self.email, self.password)

        # Obtener su id
        user_id = db_get_user_id_by_email(self.email)

        # Creación de la alerta
        db_create_alerta_by_all(user_id, self.cpv_search, self.contrato, self.palabra_clave, self.fecha1, self.fecha2, self.importe1, self.importe2)

        # Consultar si la alerta fue creada
        with engine.connect() as conn:
            alerta = conn.execute(
                text("SELECT * FROM alertas WHERE id_usuario = :user_id"),
                {"user_id": user_id}
            ).fetchone()

        self.assertIsNotNone(alerta, "La alerta no debería ser None")
        self.assertEqual(alerta["id_usuario"], user_id, "El is del usuario no coincide")

    def test_db_get_top3_recomendaciones_by_user_id(self):
        """
        Prueba la función db_get_top3_recomendaciones_by_user_id.
        """
        # Crear un usuario de prueba
        db_create_user_by_all(self.email, self.password)

        # Obtener su id
        user_id = db_get_user_id_by_email(self.email)

        # Insertar recomendaciones de prueba
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO recomendaciones (id_usuario, recomendacion, instancias)
                    VALUES (:user_id, :recomendacion, :instancias)
                """),
                [
                    {"user_id": user_id, "recomendacion": "Recomendación 1", "instancias": 5},
                    {"user_id": user_id, "recomendacion": "Recomendación 2", "instancias": 3},
                    {"user_id": user_id, "recomendacion": "Recomendación 3", "instancias": 8}
                ]
            )

        # Obtener las 3 mejores recomendaciones
        recomendaciones = db_get_top3_recomendaciones_by_user_id(user_id)
        self.assertEqual(len(recomendaciones), 3, "Se esperaban 3 recomendaciones")
        self.assertEqual(recomendaciones[0][0], "Recomendación 3", "La primera recomendación debería ser 'Recomendación 3'")

    ### PRUEBAS DE INTEGRACIÓN

    def test_login_registro_usuario(self):
        """
        Prueba la integración del registro y el inicio de sesión de un usuario.
        """
        # Registro de un nuevo usuario
        response = self.app.post(
            "/",
            data={
                "action": "register",
                "email": self.email,
                "password": self.password,
            }
        )

        # Verificar que el usuario fue creado
        user = db_get_user_by_email(self.email)
        self.assertIsNotNone(user, "El usuario no debería ser None")

        # Inicio de sesión con el usuario registrado
        response = self.app.post(
            "/",
            data={
                "action": "login",
                "email": self.email,
                "password": self.password,
            }
        )
        self.assertEqual(response.status_code, 302, "El inicio de sesión debería redirigir al usuario")

    def test_creacion_y_consulta_alertas(self):
        """
        Prueba la creación y consulta de alertas.
        """
        # Crear un usuario de prueba
        db_create_user_by_all(self.email, self.password)

        # Simular datos en la sesión
        with self.app.session_transaction() as session:
            session['email'] = self.email
            session['cpv_search'] = self.cpv_search
            session['contrato'] = self.contrato
            session['palabra_clave'] = self.palabra_clave
            session['importe1'] = self.importe1
            session['importe2'] = self.importe2
            session['fecha1'] = self.fecha1
            session['fecha2'] = self.fecha2

        # Simular la creación de una alerta mediante una solicitud POST
        response = self.app.post("/alertas/nueva_alerta")
        self.assertEqual(response.status_code, 302, "La creación de la alerta debería redirigir al usuario")

        # Consultar las alertas creadas
        user_id = db_get_user_id_by_email(self.email)
        alertas = get_alertas(user_id)

        # Verificar que se haya creado al menos una alerta
        self.assertTrue(len(alertas) > 0, "Debería haber al menos una alerta creada")

        #####################

    # def test_actualizacion_datos_usuario(self):
    #     """
    #     Prueba la actualización de datos del usuario.
    #     """
    #     # Registrar un usuario
    #     db_create_user_by_all("test@example.com", "securepassword123")

    #     # Simular inicio de sesión
    #     with self.client.session_transaction() as session:
    #         session['email'] = "test@example.com"

    #     # Actualizar el correo electrónico
    #     response = self.client.post(
    #         "/actualizar_datos",
    #         data={"email": "new_email@example.com", "password": "newpassword123"},
    #         follow_redirects=True
    #     )
    #     self.assertEqual(response.status_code, 200, "La actualización debería ser exitosa")

    #     # Verificar que los datos se hayan actualizado en la base de datos
    #     with engine.connect() as conn:
    #         user = conn.execute(text("SELECT * FROM usuarios WHERE email = :email"), {"email": "new_email@example.com"}).fetchone()
    #         self.assertIsNotNone(user, "El usuario debería haberse actualizado")
    #         self.assertEqual(user["email"], "new_email@example.com", "El correo electrónico no coincide")

    def test_eliminacion_alerta(self):
        """
        Prueba la eliminación de una alerta.
        """
        # Crear un usuario y una alerta
        db_create_user_by_all(self.email, self.password)

        # Obtener su id
        user_id = db_get_user_id_by_email(self.email)

        # Simular datos en la sesión
        with self.app.session_transaction() as session:
            session['email'] = self.email
            session['cpv_search'] = self.cpv_search
            session['contrato'] = self.contrato
            session['palabra_clave'] = self.palabra_clave
            session['importe1'] = self.importe1
            session['importe2'] = self.importe2
            session['fecha1'] = self.fecha1
            session['fecha2'] = self.fecha2

        # Simular la creación de una alerta mediante una solicitud POST
        response = self.app.post("/alertas/nueva_alerta")
        self.assertEqual(response.status_code, 302, "La creación de la alerta debería redirigir al usuario")

        # Consultar las alertas creadas
        with engine.connect() as conn:
            alerta_id = conn.execute(
                text("SELECT id FROM alertas WHERE id_usuario = :user_id"),
                {"user_id": user_id}
            ).fetchall()

        # Eliminar la alerta
        response = self.app.post(
            "/alertas/alerta/eliminar",
            data={
                "alerta_id": alerta_id[0],
            }
        )
        self.assertEqual(response.status_code, 302, "La eliminación debe redirigir al usuario")

        # Verificar que la alerta ya no exista
        with engine.connect() as conn:
            alertas = conn.execute(text("SELECT * FROM alertas WHERE id = :id"), {"id": alerta_id}).fetchone()
        self.assertEqual(alertas, None, "La alerta debería haber sido eliminada")

    ### PRUEBAS FUNCIONALES

    def test_home_page(self):
        """
        Prueba la funcionalidad de la página de inicio de sesión.
        """
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200, "La página principal debería cargarse correctamente")
        self.assertIn(b"Bienvenido", response.data, "El texto 'Bienvenido' debería estar presente")

    def test_filtro_licitaciones(self):
        """
        Prueba la funcionalidad de filtrado de licitaciones.
        """
        # Insertar datos de prueba en la base de datos
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO licitacion (CPV, Vigente_Anulada_Archivada, Estado, Tipo_de_contrato, Objeto_del_Contrato, Valor_estimado_del_contrato, Fecha_de_presentación_de_ofertas)
                    VALUES (:cpv, :vigencia, :estado, :contrato, :objeto, :importe, :fecha_limite)
                """),
                {
                    "cpv": self.cpv_search,
                    "vigencia": "Vigente",
                    "estado": "En plazo",
                    "contrato": self.contrato,
                    "objeto": "Licitación de prueba",
                    "importe": 3000,
                    "fecha_limite": "2025-10-02"
                }
            )

        # Simular datos en la sesión
        with self.app.session_transaction() as session:
            session['email'] = self.email

        # Simular la solicitud POST con datos
        response = self.app.get(
            "/datos/get_data_lici",
            data={
                "cpv_search": self.cpv_search,
                "contrato": self.contrato,
                "palabra_clave": self.palabra_clave,
                "importe1": self.importe1,
                "importe2": self.importe2,
                "fecha1": self.fecha1,
                "fecha2": self.fecha2
            }
        )

        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200, "El filtro de licitaciones debería ser exitoso")

        # Verificar que aparezca la licitación de prueba en la respuesta
        self.assertIn("Licitación de prueba", response.data.decode('utf-8'), "Debería aparecer la licitación de prueba")

        # Eliminación de licitación
        with engine.connect() as conn:
            objeto = "Licitacion de prueba"
            conn.execute(text("DELETE FROM licitacion WHERE cpv = :cpv and Objeto_del_Contrato = :objeto"), {"cpv": self.cpv_search, "objeto": objeto})

    def test_envio_correo_bienvenida(self):
        """
        Prueba la funcionalidad de envío de correo de bienvenida.
        """
        # Simular el envío de correos
        with patch('flask_app.mandar_correo') as mock_send_mail:
            # Registrar un usuario
            response = self.app.post(
                "/",
                data={
                    "action": "register",
                    "email": self.email,
                    "password": self.password,
                }
            )
            self.assertEqual(response.status_code, 302, "El registro debería redirigir al usuario")
            # Verificar que el usuario fue creado
            user = db_get_user_by_email(self.email)
            self.assertIsNotNone(user, "El usuario no debería ser None")

            # Verificar que el correo fue enviado
            mock_send_mail.assert_called_once()  # Verifica que mail.send fue llamado exactamente una vez

            # Verificar los argumentos con los que se llamó mail.send
            args, kwargs = mock_send_mail.call_args
            self.assertEqual(args[2], self.email, "El correo debería enviarse al usuario registrado")
            self.assertIn("Bienvenido", args[0], "El cuerpo del correo debería contener 'Bienvenido'")

if __name__ == "__main__":
    unittest.main()