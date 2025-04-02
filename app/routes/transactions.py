#transactions.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from pydantic import BaseModel
from uuid import uuid4, UUID  
from datetime import datetime
from app.database.models import Monto, Fecha, Ubicacion, MetodoPago, Transaccion

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.postgres import get_async_session

from app.schemas.transacciones import TransaccionUpdate


from app.database.postgres import SessionLocal
from app.database.mongo import fraudes_collection

from bson import ObjectId

def parse_document(document: dict) -> dict:
    """Convierte los ObjectId en el documento a strings."""
    for key, value in document.items():
        if isinstance(value, ObjectId):
            document[key] = str(value)
    return document

# Dependencia para la sesión de PostgreSQL
async def get_session():
    async with SessionLocal() as session:
        yield session

router = APIRouter()

# Modelo Pydantic para recibir transacción completa
class TransaccionCompleta(BaseModel):
    usuario_id: UUID
    monto: float
    moneda: str
    ciudad: str
    pais: str
    metodo_pago: str
    proveedor: str

@router.post("/registrar")
async def registrar_transaccion(data: TransaccionCompleta, session: AsyncSession = Depends(get_session)):
    transaccion_id = uuid4()

    # Insertar en montos
    monto_id = uuid4()
    await session.execute(insert(Monto).values(
        id_monto=monto_id,
        valor=data.monto,
        moneda=data.moneda
    ))

    # Insertar en fechas
    fecha_id = uuid4()
    await session.execute(insert(Fecha).values(
        id_fecha=fecha_id,
        fecha=datetime.now()
    ))

    # Insertar en ubicaciones
    ubicacion_id = uuid4()
    await session.execute(insert(Ubicacion).values(
        id_ubicacion=ubicacion_id,
        ciudad=data.ciudad,
        pais=data.pais
    ))

    # Insertar en métodos de pago
    metodo_id = uuid4()
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
            "id_transaccion": str(transaccion_id),
            "usuario_id": str(data.usuario_id),
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

@router.get("/fraudes/{usuario_id}")
async def obtener_fraudes(usuario_id: str):
    # Asegúrate de que el usuario_id se envíe como string, o convertirlo si fuera UUID
    fraudes = await fraudes_collection.find({"usuario_id": usuario_id}).to_list(100)
    if not fraudes:
        raise HTTPException(status_code=404, detail="No se encontraron fraudes para este usuario")
    
    # Parsear cada documento para convertir ObjectId a string
    fraudes_parseados = [parse_document(f) for f in fraudes]
    return {"usuario_id": usuario_id, "fraudes": fraudes_parseados}

@router.get("/usuario/{usuario_id}")
async def obtener_transacciones_usuario(usuario_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(Transaccion).where(Transaccion.usuario_id == usuario_id)
        result = await session.execute(query)
        transacciones = result.scalars().all()
        return transacciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{id_transaccion}")
async def obtener_transaccion(id_transaccion: str, session: AsyncSession = Depends(get_async_session)):
    transaccion = await session.get(Transaccion, id_transaccion)
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return transaccion

@router.get("/")
async def listar_transacciones(session: AsyncSession = Depends(get_async_session)):
    query = select(Transaccion)
    result = await session.execute(query)
    return result.scalars().all()


@router.delete("/{id_transaccion}")
async def eliminar_transaccion(id_transaccion: str, session: AsyncSession = Depends(get_async_session)):
    transaccion = await session.get(Transaccion, id_transaccion)
    if not transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    await session.delete(transaccion)
    await session.commit()
    return {"mensaje": "Transacción eliminada"}

@router.put("/{id_transaccion}")
async def actualizar_transaccion(
    id_transaccion: UUID,
    datos: TransaccionUpdate,
    session: AsyncSession = Depends(get_session)
):
    transaccion = await session.get(Transaccion, id_transaccion)
    if not transaccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada"
        )

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(transaccion, campo, valor)

    await session.commit()
    await session.refresh(transaccion)
    return transaccion



