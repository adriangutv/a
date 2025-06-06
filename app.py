from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from utils.conversacion import generar_respuesta, analizar_intencion
from utils.elevenlabs import texto_a_audio
from utils.calendar import agendar_google_meet
import os

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# ✅ Endpoint base de verificación
@app.route("/", methods=["GET"])
def home():
    return "✅ BPS E-TRUCK IA está en línea"

# 🎧 Endpoint para Twilio: reproduce el audio generado
@app.route("/twiml-bps", methods=["GET", "POST"])
def twiml_bps():
    twiml = f"""
    <Response>
        <Play>{os.getenv('DOMAIN_URL')}/static/voz_llamada.mp3</Play>
    </Response>
    """
    return Response(twiml, mimetype="text/xml")

# 🧠 Genera respuesta y voz con ElevenLabs (modo prueba manual)
@app.route("/probar-llamada", methods=["POST"])
def probar_llamada():
    data = request.get_json()
    texto_usuario = data.get("mensaje_usuario")
    telefono = data.get("telefono")

    if not texto_usuario:
        return jsonify({"error": "Falta el mensaje del usuario"}), 400

    respuesta_ia = generar_respuesta(texto_usuario)
    guardado = texto_a_audio(respuesta_ia, "static/voz_llamada.mp3")

    if not guardado:
        return jsonify({"error": "No se pudo generar la voz"}), 500

    return jsonify({
        "respuesta": respuesta_ia,
        "voz_url": f"{os.getenv('DOMAIN_URL')}/static/voz_llamada.mp3",
        "telefono": telefono
    })

# 📆 Agendar reunión directamente
@app.route("/agendar-reunion", methods=["POST"])
def agendar_reunion():
    data = request.get_json()
    nombre = data.get("nombre")
    correo = data.get("correo")
    fecha_iso = data.get("fecha_iso")

    if not nombre or not correo or not fecha_iso:
        return jsonify({"error": "Faltan datos"}), 400

    resultado = agendar_google_meet(nombre, correo, fecha_iso)
    if resultado["status"] != "success":
        return jsonify({"error": resultado["message"]}), 500

    return jsonify({
        "meet_url": resultado["meet_link"],
        "fecha": resultado["start"]
    })

# 💬 Analiza mensaje y agenda si aplica
@app.route("/mensaje", methods=["POST"])
def manejar_mensaje():
    data = request.get_json()
    mensaje = data.get("mensaje")
    nombre = data.get("nombre")
    correo = data.get("correo")

    resultado = analizar_intencion(mensaje)
    intencion = resultado.get("intencion")
    fecha_iso = resultado.get("fecha_sugerida")

    if intencion == "agendar" and fecha_iso and correo:
        agendado = agendar_google_meet(nombre, correo, fecha_iso)
        if agendado["status"] == "success":
            return jsonify({
                "respuesta": f"¡Listo {nombre}! Tu cita está agendada. Aquí tienes el enlace para conectarte: {agendado['meet_link']}",
                "enlace": agendado["meet_link"],
                "fecha": agendado["start"]
            })
        else:
            return jsonify({"respuesta": f"Error al agendar: {agendado['message']}"})

    return jsonify({"respuesta": "Gracias por tu mensaje, lo estoy revisando y te daré seguimiento."})

# 🏁 Ejecutar en Railway
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

