from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import SECRET_KEY, init_mail
from werkzeug.security import generate_password_hash, check_password_hash
from utils import limpiar_filtros, datos_licitaciones_filtrados, obtener_recomendaciones_principales, datos_consultas_filtrados, mandar_correo, db_get_user_by_email, db_create_user_by_all
from routes import alerta_bp, datos_bp, profile_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

mail = init_mail(app)

# Registrar los Blueprints
app.register_blueprint(alerta_bp, url_prefix='/alertas')
app.register_blueprint(datos_bp, url_prefix='/datos')
app.register_blueprint(profile_bp, url_prefix='/profiles')

# Ruta principal: pantalla de inicio de sesión y registro
@app.route('/', methods=['GET', 'POST'])
def login_register():
    """
    Ruta principal: pantalla de inicio de sesión y registro.

    Proceso:
        1. Si se envía un formulario (POST), obtiene la acción seleccionada ('continue', 'register' o 'login').
        2. Si la acción es 'continue', redirige al usuario a la página de inicio sin iniciar sesión.
        3. Si la acción es 'register':
            - Verifica si el usuario ya existe en la base de datos.
            - Si no existe, registra al nuevo usuario con su correo electrónico y una contraseña hasheada.
            - Envía un correo de bienvenida al usuario.
            - Inicia sesión automáticamente y redirige al usuario a la página de inicio.
        4. Si la acción es 'login':
            - Verifica las credenciales del usuario.
            - Si son correctas, inicia sesión y redirige al usuario a la página de inicio.
            - Si no son correctas, muestra un mensaje de error y redirige al formulario de inicio de sesión.
        5. Si es una solicitud GET, muestra el formulario de inicio de sesión/registro.

    Returns:
        Renderiza la plantilla 'login.html' para solicitudes GET.
        Redirige a otras rutas según la acción realizada.
    """
    if request.method == 'POST':
        action = request.form.get('action')

        # Si se elige navegar sin registro
        if action == 'continue':
            return redirect(url_for('home'))

        email = request.form.get('email')
        password = request.form.get('password')
        user = db_get_user_by_email(email)

        # Si se elige registrar
        if action == 'register':
            # Verificar si el usuario ya existe
            if user:
                flash("El usuario ya existe. Por favor, inicia sesión.")
                return redirect(url_for('login_register'))

            # Insertar nuevo usuario
            hashed_password = generate_password_hash(password)
            db_create_user_by_all(email, hashed_password)
            user = db_get_user_by_email(email)
            cuerpo = (f"Bienvenido a InnovaIRV Licitaciones, {email}")
            asunto = "Bienvenido!!!"
            mandar_correo(cuerpo, asunto, email)
            session['user_id'] = user['id']
            session['email'] = user['email']
            return redirect(url_for('home'))

        # Si se elige iniciar sesión
        elif action == 'login':
            # Comprobar si el usuario existe
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['email'] = user['email']
                return redirect(url_for('home'))
            elif not user:
                flash("Usuario no registrado")
                return redirect(url_for('login_register'))
            else:
                flash("Nombre de usuario o contraseña incorrectos.")
                return redirect(url_for('login_register'))
    return render_template('login.html')

# Ruta de inicio (home) después de iniciar sesión o elegir navegar sin registro
@app.route('/home')
def home():
    """
    Ruta de inicio (home) después de iniciar sesión o elegir navegar sin registro.

    Proceso:
        1. Obtiene el correo electrónico del usuario de la sesión (si está logueado).
        2. Limpia los filtros de búsqueda almacenados en la sesión.
        3. Obtiene los datos filtrados de licitaciones utilizando la función `datos_licitaciones_filtrados`.
        4. Obtiene las recomendaciones principales del usuario (si está logueado).
        5. Renderiza la plantilla 'index.html' con los resultados, datos de paginación, recomendaciones y el correo electrónico del usuario.

    Returns:
        Renderiza la plantilla 'index.html' con los datos necesarios.
    """
    email = session.get('email')
    limpiar_filtros()
    result, page, total_pages, has_results, total_results = datos_licitaciones_filtrados()
    recomendaciones_principales = obtener_recomendaciones_principales(email) if email else []
    return render_template('index.html', result=result, page=page, total_pages=total_pages, has_results=has_results, total_results=total_results, email=email,
        recomendaciones_principales=recomendaciones_principales)

@app.route('/consultas')
def consultas():
    """
    Ruta para mostrar las consultas preliminares.

    Proceso:
        1. Obtiene el correo electrónico del usuario de la sesión (si está logueado).
        2. Limpia los filtros de búsqueda almacenados en la sesión.
        3. Obtiene los datos filtrados de consultas utilizando la función `datos_consultas_filtrados`.
        4. Renderiza la plantilla 'consulta.html' con los resultados y datos de paginación.

    Returns:
        Renderiza la plantilla 'consulta.html' con los datos necesarios.
    """
    email = session.get('email')
    limpiar_filtros()
    result, page, total_pages, has_results, total_results = datos_consultas_filtrados()
    return render_template('consulta.html', result=result, page=page, total_pages=total_pages, has_results=has_results, total_results=total_results, email=email)

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    """
    Ruta para cerrar sesión.

    Proceso:
        1. Elimina todos los datos de la sesión.
        2. Muestra un mensaje de éxito ('flash') indicando que la sesión ha sido cerrada.
        3. Redirige al usuario al formulario de inicio de sesión.

    Returns:
        Redirige al usuario a la ruta 'login_register'.
    """
    session.clear()
    flash("Has cerrado sesión.")
    return redirect(url_for('login_register'))

@app.route('/limpiar_sesion', methods=['POST'])
def limpiar_sesion():
    """
    Ruta para limpiar los datos de la sesión.

    Proceso:
        1. Llama a la función 'limpiar_filtros' para eliminar los filtros almacenados en la sesión.
        2. Retorna una respuesta HTTP 204 (sin contenido).

    Returns:
        Respuesta HTTP 204 (sin contenido).
    """
    limpiar_filtros()
    return '', 204

if __name__ == '__main__':
    app.run(port=5004)