from flask import Flask, render_template, Blueprint, request, redirect, url_for, session
from config import get_connection  # Conexión a PostgreSQL

main = Blueprint('comprador_blueprint', __name__)

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
            return render_template('comprador/perfilComprador.html', user=user)
        else:
            return """<script> alert("Usuario no encontrado."); window.location.href = "/CULTIVARED/login"; </script>"""
    
    return """<script> alert("Por favor, primero inicie sesión."); window.location.href = "/CULTIVARED/login"; </script>"""
