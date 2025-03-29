from flask import Flask, render_template, Blueprint, request, redirect, url_for, session
from config import get_connection  
from flask import render_template, request, session
from models import db, Usuarios

# Definir el Blueprint antes de usarlo
main = Blueprint('admin_blueprint', __name__)

@main.route('/')
def admin():
    if 'logueado' in session and session['logueado']:
        conn = get_connection()
        cur = conn.cursor()
        
        # Obtener datos del usuario autenticado
        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            return render_template('administrador/administrador.html', user=user)
        else:
            return """<script> alert("Usuario no encontrado."); window.location.href = "/CULTIVARED/login"; </script>"""
    
    return """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

# Definir la ruta de perfil
@main.route('/perfil')
def perfil():
    if 'logueado' in session and session['logueado']:
        conn = get_connection()
        cur = conn.cursor()
        
        # Obtener datos del usuario autenticado
        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user:
            return render_template('administrador/perfil.html', user=user)
        else:
            return """<script> alert("Usuario no encontrado."); window.location.href = "/CULTIVARED/login"; </script>"""
    
    return """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

# Definir la ruta de transacciones
@main.route('/transacciones')
def transacciones():
    if 'logueado' in session and session['logueado']:
        # Conecta a la BD y obtener el usuario actual
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
        user = cur.fetchone()
        cur.close()
        conn.close()

        # user al render_template
        return render_template('administrador/transacciones.html', user=user)
    else:
        return """<script>alert("No estás logueado.");window.location.href="/CULTIVARED/login";</script>"""

# Definir la ruta de productos
@main.route('/productos')
def productos():
    if 'logueado' in session and session['logueado']:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        return render_template('administrador/productos.html', user=user)
    else:
        return """<script>alert("No estás logueado.");window.location.href="/CULTIVARED/login";</script>"""

# Definir la ruta de usuarios (crud)
@main.route('/crud')
def usuarios():
    if 'logueado' in session and session['logueado']:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
        user = cur.fetchone()
        cur.close()
        conn.close()

        return render_template('administrador/usuarios.html', user=user)
    else:
        return """<script>alert("No estás logueado.");window.location.href="/CULTIVARED/login";</script>"""

# Definir la ruta de editar
@main.route('/editar/<int:user_id>', methods=['GET', 'POST'])
def editar(user_id):
    # Paso 1: Verificar que el usuario esté logueado
    if 'logueado' in session and session['logueado']:
        # Conectar a la base de datos
        conn = get_connection()
        cur = conn.cursor()
        
        if request.method == 'POST':
            # Paso 2: Procesar los datos del formulario
            
            # Extraer los datos enviados desde el formulario
            # 'identificacion' se obtiene pero no se actualiza (el ID es la PK)
            identificacion = request.form.get('id')
            nombre = request.form.get('nombre')
            apellido = request.form.get('apellido')
            email = request.form.get('email')
            genero = request.form.get('genero')
            contrasena = request.form.get('contrasena')
            confirmar_contrasena = request.form.get('confirmar_contrasena')
            telefono = request.form.get('telefono')
            
            # Validación de contraseñas
            if contrasena and contrasena != confirmar_contrasena:
                cur.close()
                conn.close()
                return """<script>alert("Las contraseñas no coinciden."); window.history.back();</script>"""
            
            # Actualizar los datos del usuario en la BD (sin tocar el rol)
            cur.execute("""
                UPDATE usuarios
                SET nombre=%s, apellido=%s, email=%s, genero=%s, telefono=%s
                WHERE id=%s
            """, (nombre, apellido, email, genero, telefono, user_id))
            
            # Si se ingresó nueva contraseña, actualizarla (sin encriptar en este ejemplo)
            if contrasena and contrasena.strip():
                cur.execute("UPDATE usuarios SET contrasena=%s WHERE id=%s", (contrasena, user_id))
            
            conn.commit()
            
            # Actualizar el correo
            session['email'] = email
            cur.close()
            conn.close()
            
            return """<script>alert("Datos actualizados correctamente."); window.location.href="/ADMINISTRADOR/perfil";</script>"""
        
        else:  # Método GET: mostrar el formulario con los datos actuales
            cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if user:
                # Renderizar la plantilla editarPerfil.html pasando los datos del usuario
                return render_template('administrador/editarPerfil.html', user=user)
            else:
                return """<script>alert("Usuario no encontrado."); window.location.href="/ADMINISTRADOR/perfil";</script>"""
    else:
        return """<script>alert("No estás logueado."); window.location.href="/CULTIVARED/login";</script>"""