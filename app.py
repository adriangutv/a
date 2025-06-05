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
    audio_url = "https://URL-REAL-DE-TU-AUDIO.mp3"

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
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        respuesta = completion.choices[0].message.content
        return jsonify({"respuesta": respuesta})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

