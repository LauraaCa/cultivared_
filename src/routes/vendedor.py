from config import get_connection  # Importamos la conexión a PostgreSQL
import io
from flask import Flask, flash, render_template, Blueprint, request, redirect, send_file, url_for, session
from models import db, Producto


main = Blueprint('vendedor_blueprint', __name__)
#
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
        flash("Por favor, inicie sesión.", "warning")
        return redirect(url_for('autenticacion.login'))

    if request.method == 'POST':
        try:
            imagen_file = request.files.get('imagen')
            if not imagen_file:
                raise ValueError("Debes subir una imagen.")

            imagen_bytes = imagen_file.read()

            ide = request.form.get('idProducto')
            nombre = request.form.get('nombreProducto')
            descripcion = request.form.get('descripcionProducto')
            categoria = request.form.get('categoria')
            cantidad = request.form.get('unidades')
            precio = request.form.get('precio')
            idVendedor = session.get('id')

            if not all([ide, nombre, descripcion, categoria, cantidad, precio]):
                raise ValueError("Todos los campos son obligatorios.")

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO productos (id, nombre, descripcion, categoria, cantidad, precio, id_vendedor, imagen)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (ide, nombre, descripcion, categoria, cantidad, precio, idVendedor, imagen_bytes))

            conn.commit()
            cur.close()
            conn.close()

            return "<script>alert('Usuario registrado correctamente'); window.location.href = '/CULTIVARED/RegistroProductos';</script>"

        except Exception as e:
            flash(f"❌ Error al registrar el producto: {str(e)}", "danger")
            return redirect(url_for('vendedor_blueprint.registro_productos'))

    return redirect(url_for('vendedor_blueprint.registro_productos'))


@main.route('/imagen_producto/<int:producto_id>')
def imagen_producto(producto_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT imagen FROM productos WHERE id = %s", (producto_id,))
    imagen = cur.fetchone()
    cur.close()
    conn.close()

    if imagen and imagen[0]:
        return send_file(io.BytesIO(imagen[0]), mimetype='image/jpeg')  # O image/png si usas PNG
    else:
        return "", 204  # Sin contenido

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
    if 'id' not in session:
        return """<script> alert("Por favor, inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('/vendedor/historialPedidos.html', user=user)


@main.route('/ResumenVentas')
def resumen_ventas():
    if 'id' not in session:
        return """<script> alert("Por favor, inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE id = %s', (session['id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('/vendedor/resumenVentas.html',user=user)


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

    return render_template('/vendedor/perfil.html', user=user)

@main.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    try:
        producto = Producto.query.get(id)
        if not producto:
            flash("El producto no existe o no se pudo cargar.", "error")
            return redirect(url_for('vendedor_blueprint.mis_productos'))
        
        if request.method == 'POST':
            producto.nombre = request.form['nombreProducto']
            producto.categoria = request.form['categoria']
            producto.cantidad = request.form['cantidad']
            producto.precio = request.form['precio']
            producto.descripcion = request.form['descripcionProducto']

            imagen_file = request.files.get('imagen')
            if imagen_file and imagen_file.filename != '':
                producto.imagen = imagen_file.read()

            db.session.commit()
            flash("Producto actualizado correctamente.", "success")
            return redirect(url_for('vendedor_blueprint.mis_productos'))
        
        return render_template('vendedor/editar_producto.html', producto=producto)

    except Exception as e:
        flash(f"Error al procesar la solicitud: {str(e)}", "error")
        return redirect(url_for('vendedor_blueprint.mis_productos'))


@main.route('/productos/eliminar/<int:id>', methods=['GET','POST'])
def eliminar(id):
    producto = Producto.query.get(id)

    if not producto:
        flash("El producto no existe.", "error")
        return redirect(url_for('vendedor_blueprint.mis_productos'))

    db.session.delete(producto)
    db.session.commit()

    flash("Producto eliminado correctamente.", "success")
    return redirect(url_for('vendedor_blueprint.mis_productos'))

@main.route('/logout')
def logout():
    session.clear()  # Elimina toda la información de la sesión
    flash("Has cerrado sesión correctamente.", "success")
    return redirect('/CULTIVARED/login')
