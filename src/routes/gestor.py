from flask import Flask, render_template, Blueprint, request, redirect, url_for, session
from config import get_connection  # Importamos la conexión a PostgreSQL

main = Blueprint('gestor_blueprint', __name__)


@main.route('/')
def gestor():
    if 'logueado' in session and session['logueado']:
        conn = get_connection()
        cur = conn.cursor()
        
        # Obtener datos del usuario autenticado
        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            return render_template('gestor/perfilGestor.html', user=user)
        else:
            
            return """<script> alert("Usuario no encontrado."); window.location.href = "/CULTIVARED/login"; </script>"""
    
    return """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""


@main.route('/gestion_usuarios')
def gestion_usuarios():
    if 'logueado' in session and session['logueado']:
        rol = request.args.get('rol', 'all')  # Obtener el rol desde la URL

        conn = get_connection()
        cur = conn.cursor()

        if rol == 'all':
            cur.execute('SELECT id, nombre, apellido, genero, email, telefono, rol FROM usuarios')
        else:
            cur.execute('SELECT id, nombre, apellido, genero, email, telefono, rol FROM usuarios WHERE LOWER(rol) = %s', (rol.lower(),))

        users = cur.fetchall()
        cur.close()
        conn.close()

        print("Usuarios obtenidos:", users)  # Verifica en consola qué datos se están trayendo

        return render_template('gestor/gestionUsuarios.html', usuarios=users, selected_role=rol)
    else:
        return redirect(url_for('auth.login'))


def obtener_usuario_por_id(user_id):
    connection = get_connection()  # Asegúrate de tener tu conexión a la DB
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()
    connection.close()
    return usuario

@main.route('/GESTOR/perfil_usuario/<int:user_id>')
def perfil_usuario(user_id):
    # Aquí debes obtener los datos del usuario desde la base de datos
    user = obtener_usuario_por_id(user_id)  # Función que debes definir
    print(f"Usuario encontrado: {user}")
    if not user:
        return "Usuario no encontrado", 404
    
    return render_template('gestor/perfil_usuario.html', user=user)
