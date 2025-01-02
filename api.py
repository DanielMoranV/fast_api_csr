from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import win32com.client
from pydantic import BaseModel
import pythoncom
import pywintypes
import logging

app = FastAPI()

# Load environment variables
load_dotenv(override=True)
provider = os.getenv("PROVIDER")
data_source = os.getenv("DATA_SOURCE")
exclusive = os.getenv("EXCLUSIVE")

CONNECTION_STRING = (
    fr"Provider={provider};"
    fr"Data Source={data_source};"
    fr"Exclusive={exclusive};"
)

# Configuración de CORS
origins = [
    "http://localhost:5173",
    # Añade aquí otros orígenes permitidos si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryModel(BaseModel):
    query: str


def open_connection():
    try:
        pythoncom.CoInitialize()
        connection = win32com.client.Dispatch('ADODB.Connection')
        connection.Open(CONNECTION_STRING)
        return connection
    except Exception as e:
        raise Exception(f"Error al abrir la conexión: {e}")


@app.post("/execute_query")
def execute_query(data: QueryModel):
    connection = None
    recordset = None
    try:
        connection = open_connection()
        recordset = win32com.client.Dispatch('ADODB.Recordset')
        recordset.Open(data.query, connection)

        data = []
        while not recordset.EOF:
            row = {recordset.Fields.Item(i).Name: recordset.Fields.Item(
                i).Value for i in range(recordset.Fields.Count)}
            data.append(row)
            recordset.MoveNext()
        return {"data": data}
    except pywintypes.com_error as e:
        # Registro del error de COM
        logging.error(f"Error de COM: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error de ejecución: {str(e)}")
    except Exception as e:
        # Registro de un error general
        logging.error(f"Error inesperado: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Ocurrió un error inesperado durante la ejecución.")
    finally:
        if recordset is not None and recordset.State == 1:
            try:
                recordset.Close()
            except Exception as e:
                logging.error(f"Error al cerrar el recordset: {str(e)}")
        if connection is not None and connection.State == 1:
            try:
                connection.Close()
            except Exception as e:
                logging.error(f"Error al cerrar la conexión: {str(e)}")
