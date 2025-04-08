from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from werkzeug.security import generate_password_hash
from utils import db_update_email_from_user_by_email, db_update_password_from_user_by_email, db_delete_user, db_get_user_by_email

profile_bp = Blueprint('profile', __name__)

# Ruta para perfil
@profile_bp.route('/profile')
def profile():
    """
    Muestra la página de perfil del usuario.

    Returns:
        Renderiza la plantilla 'profile.html' con el correo electrónico del usuario.
    """
    return render_template('profile.html', email=session['email'])

# Ruta para perfil
@profile_bp.route('/mod_email', methods=['POST'])
def mod_email():
    """
    Permite al usuario cambiar su correo electrónico.

    Proceso:
        1. Recupera el correo electrónico actual del usuario desde la sesión.
        2. Obtiene el nuevo correo electrónico del formulario enviado por el usuario.
        3. Comprueba si el nuevo correo ya existe. Si existe, no modifica el correo
        3. Si no existe, actualiza el correo en la base de datos.
        4. Actualiza el correo en la sesión del usuario.
        5. Muestra un mensaje de éxito ('flash') y redirige al perfil del usuario.

    Returns:
        Redirige al perfil del usuario con un mensaje de éxito.
    """
    email = session['email']
    new_email = request.form.get('new_email', '').strip()
    email_repetido = db_get_user_by_email(new_email)
    if email_repetido:
        flash("El correo ya está en uso. Elija otro.", "error")
        return redirect('/profiles/profile')
    else:
        db_update_email_from_user_by_email(email, new_email)
        flash("Correo cambiado con éxito", "success")
    session['email'] = new_email
    return redirect('/profiles/profile')

# Ruta para perfil
@profile_bp.route('/mod_password', methods=['POST'])
def mod_password():
    """
    Permite al usuario cambiar su contraseña.

    Proceso:
        1. Recupera el correo electrónico del usuario desde la sesión.
        2. Obtiene la nueva contraseña del formulario enviado por el usuario.
        3. Hashea la nueva contraseña usando 'generate_password_hash'.
        4. Actualiza la contraseña en la base de datos.
        5. Muestra un mensaje de éxito ('flash') y redirige al perfil del usuario.

    Returns:
        Redirige al perfil del usuario con un mensaje de éxito.
    """
    email = session['email']
    new_password = request.form.get('new_password', '').strip()
    hashed_password = generate_password_hash(new_password)
    db_update_password_from_user_by_email(email, hashed_password)
    flash("Contraseña cambiada con éxito")
    return redirect('/profiles/profile')

@profile_bp.route('/mod_password_email', methods=['POST'])
def mod_password_email():
    """
    Permite a un usuario cambiar su contraseña proporcionando su correo electrónico y una nueva contraseña.

    Proceso:
        1. Recupera el correo electrónico y la nueva contraseña del formulario.
        2. Valida que ambos campos estén completos.
        3. Verifica si el usuario existe en la base de datos.
        4. Si el usuario existe, hashea la nueva contraseña y actualiza la base de datos.
        5. Muestra un mensaje de éxito o error según corresponda.

    Returns:
        Redirige a la página principal con un mensaje de éxito o error.
    """
    email = request.form.get('email')
    new_password = request.form.get('new_password')

    if not email or not new_password:
        flash("Por favor, completa todos los campos.", "error")
        return redirect('/')

    try:
        # Verificar si el usuario existe
        user = db_get_user_by_email(email)

        if not user:
            flash("El correo electrónico no está registrado.", "error")
            return redirect('/')

        # Actualizar la contraseña
        hashed_password = generate_password_hash(new_password)
        db_update_password_from_user_by_email(email, hashed_password)

        flash("Contraseña actualizada correctamente.", "success")
        return redirect('/')
    except Exception as e:
        flash(f"Error al actualizar la contraseña: {str(e)}", "error")
        return redirect('/')

# Ruta para perfil
@profile_bp.route('/delete_profile', methods=['POST'])
def delete_profile():
    """
    Permite al usuario eliminar su perfil.

    Proceso:
        1. Recupera el correo electrónico del usuario desde la sesión.
        2. Elimina al usuario de la base de datos.
        3. Limpia la sesión del usuario.
        4. Muestra un mensaje de éxito ('lash') y redirige a la página de inicio de sesión/registro.

    Returns:
        Redirige a la página de inicio de sesión/registro con un mensaje de éxito.
    """
    email = session['email']
    db_delete_user(email)
    flash("Perfil eliminado con éxito")
    session.clear()
    return redirect(url_for('login_register'))