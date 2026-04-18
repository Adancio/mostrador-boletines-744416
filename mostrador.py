import boto3
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from botocore.exceptions import BotoCoreError, ClientError

expediente = "744416"

app = FastAPI()

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
TABLE_NAME = "boletines"


@app.get("/boletines/{boletin_id}", response_class=HTMLResponse)
def obtener_boletin(boletin_id: str, correoElectronico: str):
    try:
        tabla = dynamodb.Table(TABLE_NAME)
        result = tabla.get_item(Key={"boletin_id": boletin_id})
        item = result.get("Item")
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar DynamoDB: {str(e)}")

    if not item:
        raise HTTPException(status_code=404, detail="Boletín no encontrado")

    if item["correoElectronico"] != correoElectronico:
        raise HTTPException(status_code=403, detail="Correo no autorizado")

    try:
        tabla.update_item(
            Key={"boletin_id": boletin_id},
            UpdateExpression="SET leido = :val",
            ExpressionAttributeValues={":val": True},
        )
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar boletín: {str(e)}")

    imagen_url = item["imagen_url"]
    contenido = item["contenido"]

    html = f"""
    <html>
    <head><title>Boletín {boletin_id}</title></head>
    <body>
        <h1>Boletín</h1>
        <p>{contenido}</p>
        <img src="{imagen_url}" alt="Imagen del boletín" style="max-width:600px"/>
        <br/><br/>
        <a href="{imagen_url}">Ver archivo en S3</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


if __name__ == "__main__":
    print("Servicio mostrador listo")