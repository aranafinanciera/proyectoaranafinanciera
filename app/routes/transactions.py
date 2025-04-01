from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TransaccionEntrada(BaseModel):
    usuario_id: str
    monto: float
    moneda: str
    metodo_pago: str

@router.post("/")
def analizar_transaccion(transaccion: TransaccionEntrada):
    return {
        "mensaje": "Transacción recibida",
        "score_fraude": 0.72,
        "estado": "potencial fraude" if 0.72 > 0.7 else "segura"
    }
