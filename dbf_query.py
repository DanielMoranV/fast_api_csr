import json
import sys
import logging
import win32com.client
import pythoncom
from pydantic import BaseModel
from datetime import datetime

provider = 'VFPOLEDB.1'
exclusive = 'No'


class QueryModel(BaseModel):
    query: str


def open_connection(data_source):
    try:
        pythoncom.CoInitialize()
        connection = win32com.client.Dispatch("ADODB.Connection")
        connection_string = (
            fr"Provider={provider};"
            fr"Data Source={data_source};"
            fr"Exclusive={exclusive};"
        )
        connection.Open(connection_string)
        return connection
    except Exception as e:
        raise Exception(f"Error al abrir la conexión: {e}")


def execute_query(data_source, query: str):
    connection = None
    recordset = None
    try:
        connection = open_connection(data_source)
        recordset = win32com.client.Dispatch("ADODB.Recordset")
        recordset.Open(query, connection)

        data = []
        while not recordset.EOF:
            row = {recordset.Fields.Item(i).Name: recordset.Fields.Item(
                i).Value for i in range(recordset.Fields.Count)}
            data.append(row)
            recordset.MoveNext()

        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}
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


def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Tipo no serializable")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps(
            {"success": False, "error": "Debe proporcionar data_source y una consulta como argumentos."}))
        sys.exit(1)

    data_source = sys.argv[1]
    query = sys.argv[2]
    try:
        response = execute_query(data_source, query)
        print(json.dumps(response, default=datetime_handler))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
