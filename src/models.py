from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    vendedor = db.relationship("Usuarios", backref=db.backref("productos", lazy=True))


