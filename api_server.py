from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # permite cereri din alte aplicații (ex: WordPress)

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
    comanda = request.get_json()
    client_id = comanda.get("client_id")
    produse = comanda.get("produse", [])

    if not client_id or not produse:
        return jsonify({"status": "eroare", "mesaj": "Date lipsă"}), 400

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nume_fisier = f"comanda_{timestamp}.xml"
    cale_fisier = os.path.join("comenzi", nume_fisier)

    os.makedirs("comenzi", exist_ok=True)

    root = ET.Element("comanda", attrib={"client_id": str(client_id)})

    for produs in produse:
        p_elem = ET.SubElement(root, "produs")
        ET.SubElement(p_elem, "id").text = str(produs.get("id"))
        ET.SubElement(p_elem, "nume").text = produs.get("nume")
        ET.SubElement(p_elem, "pret").text = str(produs.get("pret"))
        ET.SubElement(p_elem, "cantitate").text = str(produs.get("cantitate"))
        ET.SubElement(p_elem, "subtotal").text = str(produs.get("subtotal"))

    tree = ET.ElementTree(root)
    tree.write(cale_fisier, encoding="utf-8", xml_declaration=True)

    return jsonify({"status": "ok", "fisier": nume_fisier})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
