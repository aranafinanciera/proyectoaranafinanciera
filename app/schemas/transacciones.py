from pydantic import BaseModel
from typing import Optional

class TransaccionUpdate(BaseModel):
    estado_transaccion: Optional[str] = None