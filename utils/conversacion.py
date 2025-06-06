from openai import OpenAI
import os
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎯 Genera respuesta como asesor "Miguel" de BPS E-TRUCK
def generar_respuesta(mensaje):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asesor comercial llamado Miguel de BPS E-TRUCK. "
                    "Tu misión es detectar si el usuario tiene perfil de distribuidor fuerte, "
                    "es decir, que sea empresario o tenga experiencia comercial sólida, "
                    "y que tenga capacidad de inversión. "
                    "Si cumple con eso, responde amablemente con disposición a agendar una reunión. "
                    "Si no, responde de forma profesional pero clara que por el momento no es apto."
                )
            },
            {"role": "user", "content": mensaje},
        ]
    )
    return response.choices[0].message.content


# 📆 Analiza si hay intención de agendar una cita
def analizar_intencion(mensaje):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Tu tarea es analizar el siguiente mensaje del usuario y regresar un JSON en este formato:\n"
                    '{\n'
                    '  "intencion": "agendar" o "ninguna",\n'
                    '  "fecha_sugerida": "YYYY-MM-DDTHH:MM:SS"\n'
                    '}\n\n'
                    "Solo devuelve el JSON. Si no se menciona explícitamente una fecha, sugiere una 24 horas después del momento actual."
                )
            },
            {"role": "user", "content": mensaje},
        ]
    )

    content = response.choices[0].message.content.strip()

    # Extraer JSON con regex
    match_intencion = re.search(r'"intencion":\s*"([^"]+)"', content)
    match_fecha = re.search(r'"fecha_sugerida":\s*"([^"]+)"', content)

    return {
        "intencion": match_intencion.group(1) if match_intencion else "ninguna",
        "fecha_sugerida": match_fecha.group(1) if match_fecha else None
    }

