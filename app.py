from flask import Flask, request, jsonify
import os
import requests
from openai import OpenAI
from twilio.rest import Client

app = Flask(__name__)

# Variables de entorno
openai_api_key = os.getenv("OPENAI_API_KEY")
eleven_api_key = os.getenv("ELEVENLABS_API_KEY")
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
voice_id = os.getenv("VOICE_ID")

# Inicializar clientes
openai_client = OpenAI(api_key=openai_api_key)
twilio_client = Client(twilio_sid, twilio_token)

@app.route('/')
def index():
    return "✅ BPS E-TRUCK AI operativo"

@app.route('/llamar', methods=["POST"])
def llamar():
    data = request.json
    numero = data.get("numero")
    mensaje = data.get("mensaje")

    if not numero or not mensaje:
        return jsonify({"error": "Número y mensaje son obligatorios"}), 400

    # Generar audio con ElevenLabs
    audio = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": eleven_api_key,
            "Content-Type": "application/json"
        },
        json={
            "text": mensaje,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.7
            }
        }
    )

    if audio.status_code != 200:
        return jsonify({"error": "Fallo al generar audio con ElevenLabs"}), 500

    # Guardar el archivo de audio
    with open("voz.mp3", "wb") as f:
        f.write(audio.content)

    # TODO: subir voz.mp3 a algún servidor para generar una URL pública
    audio_url = "https://elevenlabs.io/app/voice-library?voiceId=vAxdfYVShGAQEwKYqDZR"

    # Realizar llamada con Twilio
    call = twilio_client.calls.create(
        twiml=f'<Response><Play>{audio_url}</Play></Response>',
        to=numero,
        from_=twilio_number
    )

    return jsonify({"message": "📞 Llamada realizada", "call_sid": call.sid})
@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json.get("prompt")

    if not prompt:
        return jsonify({"error": "Falta el prompt"}), 400

    try:
system_prompt = """
Eres un asesor comercial amable, persuasivo y directo de BPS E-TRUCK, una marca mexicana de camionetas eléctricas para reparto de última milla. Tu objetivo es llamar a clientes potenciales que mostraron interés y:

1. Confirmar si están disponibles para hablar.
2. Que nos platiquen a qué se dedican y qué experiencia tienen en el sector automotriz.
3. Detectar discretamente si son empresarios fuertes, inversionistas o buscan ser distribuidores de la marca.
4. Platicarles sobre nuestro grupo empresarial con más de 20 años en el sector, 5 marcas importadas de China y más de 30 agencias en México. BPS E-TRUCK está en expansión.
5. Identificar si ya conocen BPS E-TRUCK o explicar que somos una marca mexicana de camionetas eléctricas para última milla con chasis cabina y van, cargas de 600 kg a 1.5 ton, autonomías de 170–250 km, precios de $410,000 a $699,000.
6. Mencionar que la inversión mínima es de $5,000,000 en ciudades grandes o $2,800,000 en ciudades menores a 1 millón de habitantes.
7. Si preguntan qué incluye, decir que se incluye inventario, refacciones, capacitación integral (comercial, técnica y administrativa) y un enfoque sólido en servicio postventa con atención inmediata como clave.
8. Preguntar qué día y hora les queda mejor para agendar una reunión por Google Meets donde nuestro director comercial presentará el business plan.
9. Si están ocupados, enviar la info por WhatsApp y preguntar cuándo se puede volver a llamar.

Debes sonar seguro, no robótico, y responder con naturalidad. Si no desean seguir, agradéceles y despídete amablemente.
"""

        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
)

        respuesta = completion.choices[0].message.content
        return jsonify({"respuesta": respuesta})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

