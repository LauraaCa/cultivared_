from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# En tu archivo de inicialización o shell

class Usuarios(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.BigInteger, primary_key=True) 
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=False)
    genero = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    telefono = db.Column(db.String(20), unique=True, nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    contrasena = db.Column(db.String(100), nullable=False)


class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(250), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    id_vendedor = db.Column(db.BigInteger, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    imagen = db.Column(db.LargeBinary, nullable=True)
    vendedor = db.relationship("Usuarios", backref=db.backref("productos", lazy=True)) 

class Transaccion(db.Model):
    __tablename__ = "transacciones"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    total = db.Column(db.Numeric(10,2), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    usuario = db.relationship("Usuarios", backref=db.backref("transacciones", lazy=True))

# class Transaccion(db.Model):
#     __tablename__ = "transacciones"
#     id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
#     usuario_id = db.Column(db.BigInteger,
#                             db.ForeignKey("usuarios.id", ondelete="CASCADE"),
#                             nullable=False)
#     fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     total = db.Column(db.Numeric(12, 2), nullable=False)

#     usuario = db.relationship("Usuario", back_populates="transacciones")
#     items = db.relationship("TransaccionItem",
#                              back_populates="transaccion",
#                              cascade="all, delete-orphan")

class Transaccion(db.Model):
    __tablename__ = "transacciones_items"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    total = db.Column(db.Numeric(10,2), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    usuario = db.relationship("Usuarios", backref=db.backref("transacciones", lazy=True))
    items = db.relationship("TransaccionItem", back_populates="transaccion", cascade="all, delete-orphan")  # <-- esta línea

    
class Carrito(db.Model):
    __tablename__ = "carrito"
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    estado = db.Column(db.String, default='open')
    creado = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('ItemsCarrito', back_populates='carrito', cascade='all, delete-orphan')

class ItemsCarrito(db.Model):
    __tablename__ = "itemsCarrito"
    id = db.Column(db.Integer, primary_key=True)
    carrito_id = db.Column(db.Integer, db.ForeignKey('carrito.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False) 
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Numeric(10,2), nullable=False)
    agregado = db.Column(db.DateTime, default=datetime.utcnow)

    carrito = db.relationship('Carrito', back_populates='items')
    producto = db.relationship('Producto')
    __table_args__ = (db.UniqueConstraint('carrito_id', 'producto_id', name='_cart_prod_uc'),)

