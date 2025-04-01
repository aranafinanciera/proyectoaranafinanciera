from fastapi import FastAPI
from app.routes import transactions

app = FastAPI(title="Araña-Financiera API", version="1.0")

app.include_router(transactions.router, prefix="/api/transactions", tags=["Transacciones"])

@app.get("/")
def root():
    return {"message": "API Araña-Financiera funcionando"}
