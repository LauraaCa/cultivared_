from flask import Blueprint, Response, abort, render_template, request, redirect, url_for, session, flash
from config import get_connection  # Conexión a PostgreSQL

main = Blueprint('comprador_blueprint', __name__)

def _init_cart():
    """Asegura que exista session['cart']."""
    if 'cart' not in session:
        session['cart'] = {}

@main.route('/')
def comprador():
    if not session.get('logueado'):
        flash('Por favor, primero inicie sesión.', 'warning')
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
    user = cur.fetchone()
    cur.execute('SELECT * FROM productos')
    productos = cur.fetchall()
    cur.close(); conn.close()

    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('comprador/comprador.html',
                           user=user, producto=productos)

@main.route('/PERFIL')
def perfil():
    if not session.get('logueado'):
        flash('Por favor, primero inicie sesión.', 'warning')
        return redirect(url_for('auth.login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
    user = cur.fetchone()
    cur.close(); conn.close()

    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('comprador/perfilComprador.html', user=user)

@main.route('/producto/<int:producto_id>/imagen')
def imagen_producto(producto_id):
    """Sirve el blob de la imagen almacenada en productos.imagen."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT imagen FROM productos WHERE id = %s", (producto_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row or not row[0]:
        abort(404)

    # Ajusta el mimetype si usas jpg, png, etc.
    return Response(row[0], mimetype='image/png')

@main.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    _init_cart()
    cart = session['cart']
    key = str(product_id)

    # 1) Consultar stock en la BD
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT cantidad FROM productos WHERE id = %s", (product_id,))
    row = cur.fetchone()
    cur.close(); conn.close()

    stock = row[0] if row else 0
    nueva_qty = cart.get(key, 0) + 1

    # 2) Validar
    if nueva_qty > stock:
        flash(f"No puedes agregar más de {stock} unidades de este producto.", 'warning')
    else:
        cart[key] = nueva_qty
        session['cart'] = cart
        flash('Producto agregado al carrito', 'success')

    return redirect(request.referrer or url_for('comprador_blueprint.comprador'))

@main.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    _init_cart()
    cart = session['cart']
    new_qty = int(request.form.get('quantity', 0))
    key = str(product_id)

    # 1) Consultar stock
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT cantidad FROM productos WHERE id = %s", (product_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    stock = row[0] if row else 0

    # 2) Validar
    if new_qty <= 0:
        cart.pop(key, None)
        flash('Producto eliminado del carrito', 'info')
    elif new_qty > stock:
        cart[key] = stock
        flash(f"Solo quedan {stock} unidades disponibles; cantidad ajustada.", 'warning')
    else:
        cart[key] = new_qty
        flash('Cantidad actualizada', 'success')

    session['cart'] = cart
    return redirect(url_for('comprador_blueprint.carrito'))

@main.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    _init_cart()
    cart = session['cart']
    if str(product_id) in cart:
        cart.pop(str(product_id))
        session['cart'] = cart
        flash('Producto eliminado del carrito', 'info')
    return redirect(url_for('comprador_blueprint.carrito'))

@main.route('/cart/checkout', methods=['POST'])
def checkout():
    if not session.get('logueado'):
        flash('Por favor, inicia sesión primero.', 'warning')
        return redirect(url_for('auth.login'))

    _init_cart()
    cart = session['cart']
    if not cart:
        flash('Tu carrito está vacío.', 'info')
        return redirect(url_for('comprador_blueprint.comprador'))

    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1) Para cada ítem, volvemos a comprobar stock y descontar
        for pid_str, qty in cart.items():
            pid = int(pid_str)
            # Bloqueo la fila para evitar race conditions
            cur.execute("SELECT cantidad FROM productos WHERE id = %s FOR UPDATE", (pid,))
            row = cur.fetchone()
            stock = row[0] if row else 0

            if stock < qty:
                raise ValueError(f"Stock insuficiente para el producto {pid}: quedan {stock}")

            cur.execute(
                "UPDATE productos SET cantidad = cantidad - %s WHERE id = %s",
                (qty, pid)
            )

        conn.commit()
        # 2) Vaciar carrito
        session.pop('cart', None)
        flash('Compra realizada con éxito. ¡Gracias!', 'success')
    except Exception as e:
        conn.rollback()
        flash(str(e), 'danger')
    finally:
        cur.close()
        conn.close()

    return redirect(url_for('comprador_blueprint.comprador'))

@main.route('/CARRITO')
def carrito():
    if not session.get('logueado'):
        flash('Por favor, inicia sesión primero.', 'warning')
        return redirect(url_for('auth.login'))

    # Obtener usuario para la base de la plantilla
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
    user = cur.fetchone()
    cur.close(); conn.close()

    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    _init_cart()
    cart = session['cart']
    if not cart:
        return render_template('comprador/carritoComprador.html',
                               user=user,
                               carrito_items=[], carrito_total=0)

    # Traer detalles de los productos
    ids_list = [int(pid) for pid in cart.keys()]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre, descripcion, precio, imagen, cantidad FROM productos WHERE id = ANY(%s)",
        (ids_list,)
    )
    rows = cur.fetchall()
    cur.close(); conn.close()

    productos = {
        row[0]: {
            'nombre':      row[1],
            'descripcion': row[2],
            'precio':      float(row[3]),
            'imagen':      row[4],
            'stock':       row[5]
        }
        for row in rows
    }

    carrito_items = []
    total = 0
    for pid_str, qty in cart.items():
        pid = int(pid_str)
        prod = productos.get(pid)
        if not prod:
            continue
        subtotal = prod['precio'] * qty
        total += subtotal
        carrito_items.append({
            'id':         pid,
            'nombre':     prod['nombre'],
            'descripcion':prod['descripcion'],
            'imagen':     prod['imagen'],
            'cantidad':   qty,
            'stock':      prod['stock'],
            'subtotal':   subtotal
        })

    return render_template('comprador/carritoComprador.html',
                           user=user,
                           carrito_items=carrito_items,
                           carrito_total=total)