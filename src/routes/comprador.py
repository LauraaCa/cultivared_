from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config import get_connection  # Conexión a PostgreSQL

main = Blueprint('comprador_blueprint', __name__)

def _init_cart():
    """Asegura que exista session['cart']."""
    if 'cart' not in session:
        session['cart'] = {}

@main.route('/')
def comprador():
    if 'logueado' in session and session['logueado']:
        conn = get_connection()
        cur = conn.cursor()
        
        # Obtener datos del usuario autenticado
        cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
        user = cur.fetchone()
        
        cur.execute('SELECT * FROM productos')
        producto = cur.fetchall()
        
        cur.close()
        conn.close()

        if user:
            return render_template('comprador/comprador.html', user=user, producto=producto)
        else:
            return """<script> alert("Usuario no encontrado."); window.location.href = "/CULTIVARED/login"; </script>"""
    
    return """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""

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

@main.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    _init_cart()
    cart = session['cart']
    key = str(product_id)
    cart[key] = cart.get(key, 0) + 1
    session['cart'] = cart
    flash('Producto agregado al carrito', 'success')
    return redirect(request.referrer or url_for('comprador_blueprint.comprador'))

@main.route('/CARRITO')
def carrito():
    # 1) Asegura que esté logueado
    if not session.get('logueado'):
        flash('Por favor, primero inicie sesión.', 'warning')
        return redirect(url_for('auth.login'))

    # 2) Recupera al usuario para la plantilla base
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM usuarios WHERE email = %s', (session['email'],))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('auth.login'))

    # 3) Inicializa el carrito en sesión
    _init_cart()
    cart = session['cart']

    # 4) Si está vacío…
    if not cart:
        return render_template('comprador/carritoComprador.html',
                               user=user,
                               carrito_items=[], carrito_total=0)

    # 5) Trae detalles de productos en sesión
    ids_list = [int(pid) for pid in cart.keys()]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, nombre, descripcion, precio, imagen
          FROM productos
         WHERE id = ANY(%s)
        """,
        (ids_list,)
    )
    rows = cur.fetchall()
    cur.close(); conn.close()

    productos = {
        row[0]: {
            'nombre':      row[1],
            'descripcion': row[2],
            'precio':      float(row[3]),
            'imagen':      row[4]
        }
        for row in rows
    }

    # 6) Construye la lista para la plantilla
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
            'subtotal':   subtotal
        })

    # 7) Renderiza pasando también user
    return render_template('comprador/carritoComprador.html',
                           user=user,
                           carrito_items=carrito_items,
                           carrito_total=total)

@main.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    _init_cart()
    cart = session['cart']
    new_qty = int(request.form.get('quantity', 0))
    key = str(product_id)

    if new_qty > 0:
        cart[key] = new_qty
        flash('Cantidad actualizada', 'success')
    else:
        cart.pop(key, None)
        flash('Producto eliminado del carrito', 'info')

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
