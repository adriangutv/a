import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Hola desde BPS E-TRUCK IA 🤖📞</h1>'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("📥 Datos recibidos:", data)
    # Aquí en un futuro puedes invocar GPT-4o, ElevenLabs o Twilio
    return jsonify({"status": "recibido"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
