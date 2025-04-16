from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DB_PATH = 'distributie_en_gros.db'

def conectare_bd():
    return sqlite3.connect(DB_PATH)

@app.route('/api/produse', methods=['GET'])
def api_produse():
    conn = conectare_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id_produs, denumire, pret_1_10, pret_11_50, pret_peste_50 FROM produse")
    produse = cursor.fetchall()
    conn.close()
    return jsonify([
        {
            "id": p[0],
            "nume": p[1],
            "pret_1_10": p[2],
            "pret_11_50": p[3],
            "pret_peste_50": p[4]
        } for p in produse
    ])

@app.route('/api/clienti', methods=['GET'])
def api_clienti():
    conn = conectare_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id_client, denumire_firma, credit FROM clienti")
    clienti = cursor.fetchall()
    conn.close()
    return jsonify([
        {
            "id": c[0],
            "nume": c[1],
            "credit": c[2]
        } for c in clienti
    ])

@app.route('/api/comenzi', methods=['GET'])
def api_comenzi():
    conn = conectare_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id_comanda, id_client, data_comanda, status FROM comenzi")
    comenzi = cursor.fetchall()
    conn.close()
    return jsonify([
        {
            "id": c[0],
            "client_id": c[1],
            "data": c[2],
            "status": c[3]
        } for c in comenzi
    ])

@app.route('/api/comanda', methods=['POST'])
def trimite_comanda():
    if request.content_type != 'application/xml':
        return "Unsupported Media Type", 415

    try:
        xml_data = request.data.decode('utf-8')
        root = ET.fromstring(xml_data)

        client_id = root.findtext('Client')
        total = root.findtext('Total')
        produse_elem = root.find('Produse')

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        nume_fisier = f"comanda_{timestamp}.xml"
        os.makedirs("comenzi", exist_ok=True)
        cale_fisier = os.path.join("comenzi", nume_fisier)

        with open(cale_fisier, 'w', encoding='utf-8') as f:
            f.write(xml_data)

        print(f"[✔] Comandă salvată: {nume_fisier}")
        return "Comanda a fost trimisă cu succes!", 200

    except Exception as e:
        print("[Eroare XML]", str(e))
        return f"Eroare la procesare XML: {e}", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
