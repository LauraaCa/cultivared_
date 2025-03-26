from flask import Flask, render_template, Blueprint, request, redirect, url_for, session
from config import get_connection  # Importamos la conexión a PostgreSQL

main = Blueprint('vendedor_blueprint', __name__)

@main.route('/')
def vendedor():
    if 'logueado' not in session or not session['logueado']:
        return """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

    conn = get_connection()
    cur = conn.cursor()
    
    # Obtener datos del usuario autenticado
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
    user = cur.fetchone()
    
    cur.close()
    conn.close()

    if user:
        return render_template('vendedor/vendedor.html', user=user)
    else:
        return """<script> alert("Usuario no encontrado."); window.location.href = "/CULTIVARED/login"; </script>"""


@main.route('/RegistroProductos')
def registro_productos():
    if 'id' not in session:
        return """<script> alert("Por favor, inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('/vendedor/regitrosProducto.html', user=user)


@main.route('/formularioProductos', methods=['GET', 'POST'])
def form():
    if 'id' not in session:
        return """<script> alert("Por favor, inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

    if request.method == 'POST':
        ide = request.form['idProducto']
        nombre = request.form['nombreProducto']
        descripcion = request.form['descripcionProducto']
        categoria = request.form['categoria']
        cantidad = request.form['unidades']
        precio = request.form['precio']
        idVendedor = session.get('id')

        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO productos (id, nombre, descripcion, categoria, cantidad, precio, id_vendedor)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (ide, nombre, descripcion, categoria, cantidad, precio, idVendedor))

                conn.commit()
                cur.close()
                conn.close()

                return "<script>alert('Producto registrado correctamente'); window.location.href = '/VENDEDOR';</script>"
            except Exception as e:
                return f"<script>alert('Error al registrar el producto: {str(e)}'); window.location.href = '/VENDEDOR/registroProductos';</script>"
        else:
            return "<script>alert('Error: No se pudo conectar a la base de datos.'); window.location.href = '/VENDEDOR/registroProductos';</script>"

    return redirect(url_for('vendedor'))


@main.route('/MisProductos')
def mis_productos():
    if 'id' not in session:
        return """<script> alert("Por favor, inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

    conn = get_connection()
    cur = conn.cursor()         
    usuario_id = session['id']
    
    cur.execute('SELECT * FROM productos WHERE id_vendedor = %s', (usuario_id,))
    data = cur.fetchall()                       

    cur.execute('SELECT * FROM usuarios WHERE id = %s', (usuario_id,))
    user = cur.fetchone()
    
    cur.close()
    conn.close()

    return render_template('/vendedor/crudProductos.html', produ=data, user=user)
                

@main.route('/HistorialPedidos')
def historial_pedidos():
    return render_template('/vendedor/historialPedidos.html')


@main.route('/ResumenVentas')
def resumen_ventas():
    return render_template('/vendedor/resumenVentas.html')


@main.route('/MiPerfil')
def mi_perfil():
    if 'id' not in session:
        return """<script> alert("Por favor, inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('/vendedor/perfilVendedor.html', user=user)
