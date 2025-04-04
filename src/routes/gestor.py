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
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('gestor/perfil_usuario.html', user=user)

@main.route('/dashboard')
def dashboard():
    conn = get_connection()
    cur = conn.cursor()

    # 🔹 1. Total de vendedores y compradores
    cur.execute("""
        SELECT 
            COUNT(CASE WHEN rol = 'vendedor' THEN 1 END) AS total_vendedores,
            COUNT(CASE WHEN rol = 'comprador' THEN 1 END) AS total_compradores
        FROM usuarios;
    """)
    total_vendedores, total_compradores = cur.fetchone()

    # 🔹 2. Ventas realizadas por cada vendedor
    cur.execute("""
        SELECT u.nombre, COUNT(p.id) AS total_ventas
        FROM usuarios u
        JOIN productos p ON u.id = p.id_vendedor
        GROUP BY u.nombre
        ORDER BY total_ventas DESC;
    """)
    ventas_por_vendedor = cur.fetchall()

    # 🔹 3. Productos más vendidos
    cur.execute("""
        SELECT nombre, cantidad FROM productos ORDER BY cantidad DESC LIMIT 5;
    """)
    productos_mas_vendidos = cur.fetchall()

    # 🔹 4. Total de ingresos generados
    cur.execute("""
        SELECT SUM(precio * cantidad) FROM productos;
    """)
    total_ingresos = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template(
        'gestor/dashboard.html', 
        total_vendedores=total_vendedores, 
        total_compradores=total_compradores,
        ventas_por_vendedor=ventas_por_vendedor,
        productos_mas_vendidos=productos_mas_vendidos,
        total_ingresos=total_ingresos
    )


@main.route('/inventario_usuario/<int:user_id>')
def inventario_usuario(user_id):
    conn = get_connection()
    cur = conn.cursor()

    # Traer productos registrados por ese usuario
    cur.execute('SELECT * FROM productos WHERE id_vendedor = %s', (user_id,))
    productos = cur.fetchall()

    # Traer info del usuario (opcional)
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    return render_template('gestor/inventarioUsuario.html', produ=productos, user=user)