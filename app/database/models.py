#models.py
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from app.database.postgres import Base
from sqlalchemy.dialects.postgresql import UUID


class Monto(Base):
    __tablename__ = "montos"
    id_monto = Column(UUID(as_uuid=True), primary_key=True)
    valor = Column(Float, nullable=False)
    moneda = Column(String(3), nullable=False, default="MXN")

class Fecha(Base):
    __tablename__ = "fechas"
    id_fecha = Column(UUID(as_uuid=True), primary_key=True)
    fecha = Column(DateTime)

class Ubicacion(Base):
    __tablename__ = "ubicaciones"
    id_ubicacion = Column(UUID(as_uuid=True), primary_key=True)
    ciudad = Column(String(100))
    pais = Column(String(100))

class MetodoPago(Base):
    __tablename__ = "metodos_pago"
    id_metodo_pago = Column(UUID(as_uuid=True), primary_key=True)
    nombre = Column(String(50), nullable=False)
    proveedor = Column(String(50))

class Transaccion(Base):
    __tablename__ = "transacciones"
    id_transaccion = Column(UUID(as_uuid=True), primary_key=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False)
    monto_id = Column(UUID(as_uuid=True), ForeignKey("montos.id_monto"), nullable=False)
    fecha_id = Column(UUID(as_uuid=True), ForeignKey("fechas.id_fecha"), nullable=False)
    ubicacion_id = Column(UUID(as_uuid=True), ForeignKey("ubicaciones.id_ubicacion"), nullable=False)
    metodo_pago_id = Column(UUID(as_uuid=True), ForeignKey("metodos_pago.id_metodo_pago"), nullable=False)
    estado_transaccion = Column(String, default="pendiente")
