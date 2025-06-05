from flask import Flask, request, jsonify, Response
from utils.conversacion import generar_respuesta, analizar_intencion
from utils.elevenlabs import texto_a_audio
from utils.calendar import agendar_google_meet
import os

app = Flask(__name__)

# ✅ Endpoint de prueba para verificar funcionamiento general
@app.route("/", methods=["GET"])
def home():
    return "✅ BPS E-TRUCK IA está en línea"

# 🎧 Endpoint para Twilio: reproducir la última respuesta generada en voz
@app.route("/twiml-bps", methods=["GET", "POST"])
def twiml_bps():
    twiml = f"""
    <Response>
        <Play>{os.getenv('DOMAIN_URL')}/static/voz_llamada.mp3</Play>
    </Response>
    """
    return Response(twiml, mimetype="text/xml")

# 🧠 Ruta para generar respuesta IA + voz desde texto
@app.route("/probar-llamada", methods=["GET"])
def probar_llamada():
    texto_usuario = request.args.get("mensaje", "")
    if not texto_usuario:
        return jsonify({"error": "Falta el mensaje del usuario"}), 400

    respuesta_ia = generar_respuesta(texto_usuario)
    guardado = texto_a_audio(respuesta_ia, "static/voz_llamada.mp3")

    if not guardado:
        return jsonify({"error": "No se pudo generar la voz"}), 500

    return jsonify({
        "respuesta": respuesta_ia,
        "voz_url": f"{os.getenv('DOMAIN_URL')}/static/voz_llamada.mp3"
    })

# 📆 Endpoint para agendar una reunión por Google Meet manualmente
@app.route("/agendar-reunion", methods=["POST"])
def agendar_reunion():
    data = request.json
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

# 🧠 Endpoint para detectar intención del mensaje y agendar si aplica
@app.route("/mensaje", methods=["POST"])
def manejar_mensaje():
    data = request.json
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

# 🏁 Ejecutar en local
if __name__ == "__main__":
    app.run(debug=True)
