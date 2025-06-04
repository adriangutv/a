import os
import requests
from flask import Flask, request, jsonify
from openai import OpenAI
from twilio.rest import Client

app = Flask(__name__)

# Carga de variables de entorno desde Railway
openai_api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("VOICE_ID")
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")

client = OpenAI(api_key=openai_api_key)

@app.route('/')
def index():
    return "🚀 BPS E-TRUCK IA está en línea"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        nombre = data.get("nombre", "cliente")
        telefono = data.get("telefono")

        print(f"📩 Webhook recibido: {data}")

        # Generar texto con GPT-4o
        prompt = f"Saluda a {nombre} cordialmente y explícale que eres BPS E-TRUCK IA, el asistente virtual que puede ayudarle a agendar una prueba de manejo de su camioneta eléctrica. Sé breve y profesional."

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un asistente comercial profesional de la marca BPS E-TRUCK"},
                {"role": "user", "content": prompt}
            ]
        )

        texto = response.choices[0].message.content.strip()
        print(f"🧠 GPT-4o respondió: {texto}")

        # Convertir texto a audio con ElevenLabs
        audio = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": elevenlabs_api_key,
                "Content-Type": "application/json"
            },
            json={
                "text": texto,
                "model_id": "eleven_monolingual_v1"
            }
        )

        if audio.status_code != 200:
            print("❌ Error al generar audio con ElevenLabs")
            return jsonify({"error": "Audio generation failed"}), 500

        with open("mensaje.mp3", "wb") as f:
            f.write(audio.content)

        # Aquí necesitarás subir `mensaje.mp3` a una URL pública (reemplaza esta línea)
        audio_url = "https://tu-servidor.com/mensaje.mp3"  # TODO: reemplazar

        # Llamada telefónica usando Twilio
        twilio = Client(twilio_sid, twilio_token)
        llamada = twilio.calls.create(
            to=telefono,
            from_=twilio_phone,
            twiml=f'<Response><Play>{audio_url}</Play></Response>'
        )

        print(f"📞 Llamada realizada a {telefono}")

        return jsonify({"status": "Llamada en proceso", "texto": texto}), 200

    except Exception as e:
        print("💥 Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)

