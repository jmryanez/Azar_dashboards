#!/usr/bin/env python3
"""
================================================================================
SERVIDOR LOCAL DE SINCRONIZACIÓN Y DASHBOARD: AZAR CHILE
================================================================================
Proporciona el backend local para servir la aplicación web y ejecutar la
sincronización con las páginas oficiales de Polla y Lotería sin bloqueos CORS.
================================================================================
"""

import os
import sys
import json
import webbrowser
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "motores"))
import actualizador_oficial

PORT = 8000

class AzarDashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        # Habilitar CORS universal para llamadas locales y file://
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With, Authorization')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            resp = {
                "status": "online",
                "message": "Servidor de sincronización oficial activo",
                "base_dir": BASE_DIR
            }
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return
        super().do_GET()

    def do_POST(self):
        if self.path in ['/api/actualizar/loto', '/api/actualizar/loto/']:
            print("\n🔄 [API] Solicitud recibida: Actualizar LOTO desde Polla Chilena...")
            try:
                import importlib
                importlib.reload(actualizador_oficial)
                result = actualizador_oficial.actualizar_loto()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                print("✅ [API] LOTO actualizado con éxito:", result.get("ultimo_sorteo"))
            except Exception as e:
                print("❌ [API] Error actualizando LOTO:", e)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
            return

        elif self.path in ['/api/actualizar/kino', '/api/actualizar/kino/']:
            print("\n🔄 [API] Solicitud recibida: Actualizar KINO desde Lotería de Concepción...")
            try:
                import importlib
                importlib.reload(actualizador_oficial)
                result = actualizador_oficial.actualizar_kino()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                print("✅ [API] KINO actualizado con éxito:", result.get("ultimo_sorteo"))
            except Exception as e:
                print("❌ [API] Error actualizando KINO:", e)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    server = None
    port = PORT
    for p in range(8000, 8010):
        try:
            server = ThreadingHTTPServer(('127.0.0.1', p), AzarDashboardHandler)
            port = p
            break
        except OSError:
            continue

    if not server:
        print("[ERROR] No se pudo encontrar un puerto libre entre 8000 y 8010.")
        return

    url = f"http://127.0.0.1:{port}/index.html"
    print("=" * 65)
    print("🚀 SERVIDOR LOCAL AZAR CHILE INICIADO")
    print(f"📡 URL del Dashboard: {url}")
    print("=" * 65)
    print("Presiona Ctrl+C para detener el servidor.\n")
    
    # Abrir navegador tras 1 segundo si no se especifica --no-browser
    if '--no-browser' not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo servidor...")
        server.server_close()

if __name__ == "__main__":
    run_server()
