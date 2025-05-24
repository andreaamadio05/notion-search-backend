from flask import Flask, request, jsonify, send_file
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

app = Flask(__name__)

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

@app.route("/buscar", methods=["POST"])
def buscar():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
            
        pregunta = data.get("pregunta", "").lower()
        if not pregunta:
            return jsonify({"error": "La pregunta es requerida"}), 400

        query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(query_url, headers=headers)
        response.raise_for_status()
        results = response.json().get("results", [])

        encontrados = []
        
        for item in results:
            props = item.get("properties", {})
            fragmento = props.get("Fragmento", {}).get("rich_text", [])
            if fragmento:
                texto = fragmento[0]["text"]["content"]
                if pregunta in texto.lower():
                    episodio = props.get("Episodio", {}).get("title", [{}])[0].get("text", {}).get("content", "")
                    minuto = props.get("Minuto", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
                    url = props.get("URL", {}).get("url", "")
                    encontrados.append({
                        "episodio": episodio,
                        "minuto": minuto,
                        "fragmento": texto[:300],
                        "url": url
                    })
        return jsonify({"resultados": encontrados})
    except requests.RequestException as e:
        return jsonify({"error": "Error al contactar Notion API"}), 503
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500
@app.route("/")
def home():
    return send_file("probar.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
