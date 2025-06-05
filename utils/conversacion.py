# utils/conversacion.py
import openai
import os
import re
from datetime import datetime, timedelta

openai.api_key = os.getenv("OPENAI_API_KEY")

def generar_respuesta(mensaje):
    respuesta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Eres un asesor comercial llamado Miguel de BPS E-TRUCK. Analiza si el usuario tiene perfil de distribuidor fuerte y responde solo si vale la pena agendar. Sé amable, profesional, pero claro."},
            {"role": "user", "content": mensaje},
        ]
    )
    return respuesta.choices[0].message.content

def analizar_intencion(mensaje):
    respuesta = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Tu tarea es detectar si el usuario quiere agendar una cita y en qué fecha. Si no lo pide, di 'ninguna'. Regresa en JSON con intencion ('agendar' o 'ninguna') y fecha_sugerida en ISO 8601 si aplica."},
            {"role": "user", "content": mensaje},
        ]
    )
    texto = respuesta.choices[0].message.content

    match = re.search(r'"intencion":\s*"(.*?)"', texto)
    intencion = match.group(1) if match else "ninguna"

    match_fecha = re.search(r'"fecha_sugerida":\s*"(.*?)"', texto)
    fecha_sugerida = match_fecha.group(1) if match_fecha else None

    return {
        "intencion": intencion,
        "fecha_sugerida": fecha_sugerida
    }

