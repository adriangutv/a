from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
import openai
import requests
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = os.getenv("VOICE_ID")

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    response.say("Hola, gracias por comunicarte con BPS E-TRUCK. ¿Puedes decirme tu nombre, por favor?", 
                 language="es-MX", voice="Polly.Conchita")
    response.record(timeout=5, transcribe=True, maxLength=6, action="/process")
    return Response(str(response), mimetype="text/xml")

@app.route("/process", methods=["POST"])
def process():
    transcribed = request.form.get("TranscriptionText", "")
    prompt = f"Actúa como asesor de ventas de BPS E-TRUCK y responde en tono profesional. El cliente dijo: {transcribed}"

    completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    reply = completion.choices[0].message.content.strip()

    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": reply,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    audio = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}", headers=headers, json=payload)

    with open("static/reply.mp3", "wb") as f:
        f.write(audio.content)

    response = VoiceResponse()
    response.play("https://tu-dominio.railway.app/static/reply.mp3")  # Cambiar por dominio real
    return Response(str(response), mimetype="text/xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
