from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from app.database.models import Monto, Fecha, Ubicacion, MetodoPago, Transaccion



from app.database.postgres import SessionLocal
from app.database.mongo import fraudes_collection

# Dependencia para la sesión de PostgreSQL
async def get_session():
    async with SessionLocal() as session:
        yield session

router = APIRouter()

# Modelo Pydantic para recibir transacción completa
class TransaccionCompleta(BaseModel):
    usuario_id: str
    monto: float
    moneda: str
    ciudad: str
    pais: str
    metodo_pago: str
    proveedor: str

@router.post("/registrar")
async def registrar_transaccion(data: TransaccionCompleta, session: AsyncSession = Depends(get_session)):
    transaccion_id = str(uuid4())

    # Insertar en montos
    monto_id = str(uuid4())
    await session.execute(insert(Monto).values(
        id_monto=monto_id,
        valor=data.monto,
        moneda=data.moneda
    ))

    # Insertar en fechas
    fecha_id = str(uuid4())
    await session.execute(insert(Fecha).values(
        id_fecha=fecha_id,
        fecha=datetime.now()
    ))

    # Insertar en ubicaciones
    ubicacion_id = str(uuid4())
    await session.execute(insert(Ubicacion).values(
        id_ubicacion=ubicacion_id,
        ciudad=data.ciudad,
        pais=data.pais
    ))

    # Insertar en métodos de pago
    metodo_id = str(uuid4())
    await session.execute(insert(MetodoPago).values(
        id_metodo_pago=metodo_id,
        nombre=data.metodo_pago,
        proveedor=data.proveedor
    ))

    # Insertar transacción principal
    await session.execute(insert(Transaccion).values(
        id_transaccion=transaccion_id,
        usuario_id=data.usuario_id,
        monto_id=monto_id,
        fecha_id=fecha_id,
        ubicacion_id=ubicacion_id,
        metodo_pago_id=metodo_id,
        estado_transaccion="pendiente"
    ))

    await session.commit()

    # Evaluar posible fraude (regla simple)
    if data.monto > 10000:
        fraude = {
            "id_transaccion": transaccion_id,
            "usuario_id": data.usuario_id,
            "monto": data.monto,
            "ubicacion": data.ciudad,
            "metodo_pago": data.metodo_pago,
            "detalles": {
                "motivo": "Monto alto",
                "modelo_deteccion": "Regla simple",
                "score_fraude": 0.91
            },
            "fecha_detectado": datetime.now().isoformat()
        }
        await fraudes_collection.insert_one(fraude)

    return {"mensaje": "Transacción registrada", "id_transaccion": transaccion_id}
