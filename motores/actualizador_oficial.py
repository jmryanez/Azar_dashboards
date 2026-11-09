#!/usr/bin/env python3
"""
================================================================================
ACTUALIZADOR OFICIAL DE BASES DE DATOS: LOTO & KINO CHILE
================================================================================
Descarga los resultados directamente desde las APIs oficiales:
- LOTO: Polla Chilena de Beneficencia (https://www.polla.cl)
- KINO: Lotería de Concepción (https://estkino.loteria.cl)

Actualiza los archivos en datos/, re-ejecuta los motores Walk-Forward
y compila automáticamente auditoria_walkforward/auditoria_data.js.
================================================================================
"""

import os
import sys
import json
import csv
import math
import time
import zipfile
import io
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS_DIR = os.path.join(BASE_DIR, "datos")
AUDIT_DIR = os.path.join(BASE_DIR, "auditoria_walkforward")
AUDIT_JS_PATH = os.path.join(AUDIT_DIR, "auditoria_data.js")

# Headers oficiales
POLLA_URL = "https://www.polla.cl/es/get/draw/with/prizes"
POLLA_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
}

KINO_URL = "https://estkino.loteria.cl/api/estadistica/download"
KINO_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://estkino.loteria.cl/estadistica'
}

def save_excel_dual(base_filename: str, records: list, fieldnames: list, sheet_title: str):
    """Guarda tanto .xlsx como .xlsm para compatibilidad total."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_title
    ws.append(fieldnames)
    
    for r in records:
        row = []
        for f in fieldnames:
            val = r.get(f, "")
            if isinstance(val, str) and val.isdigit():
                val = int(val)
            row.append(val)
        ws.append(row)
        
    for ext in [".xlsx", ".xlsm"]:
        path = os.path.join(DATOS_DIR, f"{base_filename}{ext}")
        wb.save(path)

def recompile_audit_js():
    """Compila auditoria_walkforward/auditoria_data.js con los 3 métodos independientes para LOTO y KINO."""
    def load_csv(name):
        path = os.path.join(AUDIT_DIR, name)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return list(csv.DictReader(f))
        return []

    def load_json(name):
        path = os.path.join(AUDIT_DIR, name)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error cargando {name}:", e)
        return {}

    loto_m1_data = load_csv("historial_walkforward_loto_m1.csv") or load_csv("historial_walkforward_loto.csv")
    loto_m2_data = load_csv("historial_walkforward_loto_m2.csv")
    loto_m3_data = load_csv("historial_walkforward_loto_m3.csv")

    kino_m1_data = load_csv("historial_walkforward_kino_m1.csv") or load_csv("historial_walkforward_kino.csv")
    kino_m2_data = load_csv("historial_walkforward_kino_m2.csv")
    kino_m3_data = load_csv("historial_walkforward_kino_m3.csv")

    loto_m1_brain = load_json("loto_brain_state_m1.json") or load_json("loto_brain_state.json")
    loto_m2_brain = load_json("loto_brain_state_m2.json")
    loto_m3_brain = load_json("loto_brain_state_m3.json")

    kino_m1_brain = load_json("kino_brain_state_m1.json") or load_json("kino_brain_state.json")
    kino_m2_brain = load_json("kino_brain_state_m2.json")
    kino_m3_brain = load_json("kino_brain_state_m3.json")

    with open(AUDIT_JS_PATH, 'w', encoding='utf-8') as f:
        f.write('// Datos precargados de simulación Walk-Forward y Métodos M1, M2, M3 (Actualizado automáticamente)\n')
        # Compatibilidad base
        f.write('window.LOTO_AUDIT_DATA = ' + json.dumps(loto_m1_data, ensure_ascii=False) + ';\n')
        f.write('window.KINO_AUDIT_DATA = ' + json.dumps(kino_m1_data, ensure_ascii=False) + ';\n')
        f.write('window.LOTO_BRAIN_STATE = ' + json.dumps(loto_m1_brain, ensure_ascii=False) + ';\n')
        f.write('window.KINO_BRAIN_STATE = ' + json.dumps(kino_m1_brain, ensure_ascii=False) + ';\n')

        # LOTO Métodos 1, 2 y 3
        f.write('window.LOTO_DATA_M1 = window.LOTO_AUDIT_DATA;\n')
        f.write('window.LOTO_BRAIN_M1 = window.LOTO_BRAIN_STATE;\n')
        f.write('window.LOTO_DATA_M2 = ' + json.dumps(loto_m2_data, ensure_ascii=False) + ';\n')
        f.write('window.LOTO_BRAIN_M2 = ' + json.dumps(loto_m2_brain, ensure_ascii=False) + ';\n')
        f.write('window.LOTO_DATA_M3 = ' + json.dumps(loto_m3_data, ensure_ascii=False) + ';\n')
        f.write('window.LOTO_BRAIN_M3 = ' + json.dumps(loto_m3_brain, ensure_ascii=False) + ';\n')

        # KINO Métodos 1, 2 y 3
        f.write('window.KINO_DATA_M1 = window.KINO_AUDIT_DATA;\n')
        f.write('window.KINO_BRAIN_M1 = window.KINO_BRAIN_STATE;\n')
        f.write('window.KINO_DATA_M2 = ' + json.dumps(kino_m2_data, ensure_ascii=False) + ';\n')
        f.write('window.KINO_BRAIN_M2 = ' + json.dumps(kino_m2_brain, ensure_ascii=False) + ';\n')
        f.write('window.KINO_DATA_M3 = ' + json.dumps(kino_m3_data, ensure_ascii=False) + ';\n')
        f.write('window.KINO_BRAIN_M3 = ' + json.dumps(kino_m3_brain, ensure_ascii=False) + ';\n')

def actualizar_loto() -> dict:
    """Descarga de Polla Chilena, actualiza base LOTO, corre motor y compila JS."""
    t0 = time.time()
    page_size = 20
    
    # 1. Consultar página 1 y total de resultados
    payload1 = {"gameId": "5271", "numDraws": page_size, "extraArgs": {"currentPage": 1}}
    req = urllib.request.Request(POLLA_URL, data=json.dumps(payload1).encode('utf-8'), headers=POLLA_HEADERS, method='POST')
    with urllib.request.urlopen(req, timeout=15) as resp:
        data1 = json.loads(resp.read().decode('utf-8'))
        
    total_results = data1.get("totalResults", 0)
    total_pages = math.ceil(total_results / page_size) if total_results else 275
    
    records_dict = {}
    
    def parse_item(item):
        draw_num = item.get("drawNumber")
        date_short = item.get("drawDate") or ""
        raw_results = item.get("results")
        if not raw_results:
            return None
        main_nums = [int(r['number']) for r in raw_results[:6]]
        main_nums.sort()
        comodin = int(raw_results[6]['number']) if len(raw_results) > 6 else ""
        num_str = ", ".join(map(str, main_nums)) + (f" | {comodin}" if comodin != "" else "")
        return {
            "Juego": "LOTO",
            "Sorteo": draw_num,
            "Fecha": f"{date_short} 21:00" if date_short else "",
            "Números Ganadores": num_str,
            "Num_1": main_nums[0], "Num_2": main_nums[1], "Num_3": main_nums[2],
            "Num_4": main_nums[3], "Num_5": main_nums[4], "Num_6": main_nums[5],
            "Comodín": comodin
        }

    for item in data1.get("results", []):
        parsed = parse_item(item)
        if parsed and parsed["Sorteo"]:
            records_dict[parsed["Sorteo"]] = parsed
            
    def fetch_p(p):
        payload = {"gameId": "5271", "numDraws": page_size, "extraArgs": {"currentPage": p}}
        rq = urllib.request.Request(POLLA_URL, data=json.dumps(payload).encode('utf-8'), headers=POLLA_HEADERS, method='POST')
        with urllib.request.urlopen(rq, timeout=15) as rs:
            return json.loads(rs.read().decode('utf-8')).get("results", [])

    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(fetch_p, p): p for p in range(2, total_pages + 1)}
        for f in as_completed(futures):
            try:
                for item in f.result():
                    parsed = parse_item(item)
                    if parsed and parsed["Sorteo"]:
                        records_dict[parsed["Sorteo"]] = parsed
            except Exception:
                pass
                
    valid_records = sorted(records_dict.values(), key=lambda r: int(r["Sorteo"]) if str(r["Sorteo"]).isdigit() else -1, reverse=True)
    
    fieldnames = ["Juego", "Sorteo", "Fecha", "Números Ganadores", "Num_1", "Num_2", "Num_3", "Num_4", "Num_5", "Num_6", "Comodín"]
    save_excel_dual("resultados_loto", valid_records, fieldnames, "Resultados Loto")
    
    # 2. Ejecutar motores LOTO (Métodos 1, 2 y 3)
    sys.path.insert(0, os.path.join(BASE_DIR, "motores"))
    import loto_engine_metodo1, loto_engine_metodo2, loto_engine_metodo3
    print("Corriendo LOTO Método 1...")
    loto_engine_metodo1.main()
    print("Corriendo LOTO Método 2...")
    loto_engine_metodo2.main()
    print("Corriendo LOTO Método 3...")
    loto_engine_metodo3.main()
    
    # 3. Recompilar JS con todos los métodos
    recompile_audit_js()
    
    # Cargar los datos auditados para retornar resumen
    loto_csv = os.path.join(AUDIT_DIR, "historial_walkforward_loto.csv")
    with open(loto_csv, 'r', encoding='utf-8') as f:
        audit_rows = list(csv.DictReader(f))
        
    latest_draw = valid_records[0] if valid_records else {}
    return {
        "success": True,
        "juego": "LOTO",
        "total_sorteos_validos": len(valid_records),
        "total_auditados": len(audit_rows),
        "ultimo_sorteo": latest_draw.get("Sorteo", ""),
        "fecha_ultimo_sorteo": latest_draw.get("Fecha", ""),
        "numeros_ganadores": latest_draw.get("Números Ganadores", ""),
        "tiempo_segundos": round(time.time() - t0, 1)
    }

def actualizar_kino() -> dict:
    """Descarga de Lotería de Concepción, actualiza base KINO, corre motor y compila JS."""
    t0 = time.time()
    req = urllib.request.Request(KINO_URL, headers=KINO_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        
    zf = zipfile.ZipFile(io.BytesIO(data))
    shared_strings = []
    if 'xl/sharedStrings.xml' in zf.namelist():
        ss_root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
        ns_ss = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        for si in ss_root.findall('m:si', ns_ss):
            t_elem = si.find('m:t', ns_ss)
            if t_elem is not None and t_elem.text:
                shared_strings.append(t_elem.text)
            else:
                shared_strings.append("".join([t.text for t in si.findall('.//m:t', ns_ss) if t.text]))

    sheet1_xml = zf.read('xl/worksheets/sheet1.xml')
    s_root = ET.fromstring(sheet1_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

    records = []
    for r in s_root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        cells = {}
        for c in r.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            col_letters = ''.join([ch for ch in c.attrib.get('r', '') if ch.isalpha()])
            t = c.attrib.get('t')
            v = c.find('main:v', ns)
            val = v.text if v is not None else ''
            if t == 's' and val.isdigit() and int(val) < len(shared_strings):
                val = shared_strings[int(val)]
            cells[col_letters] = val.strip()

        sorteo = cells.get('A', '')
        if sorteo.isdigit():
            fecha = cells.get('B', '')
            nums = []
            for col_idx in range(ord('C'), ord('P') + 1):
                v_str = cells.get(chr(col_idx), '')
                if v_str.isdigit():
                    nums.append(int(v_str))
            nums.sort()
            rec = {
                "Juego": "KINO",
                "Sorteo": int(sorteo),
                "Fecha": fecha,
                "Números Ganadores": ", ".join(map(str, nums)) if nums else "Resultados no disponible"
            }
            for idx in range(1, 15):
                rec[f"Num_{idx}"] = nums[idx - 1] if len(nums) >= idx else ""
            records.append(rec)

    records.sort(key=lambda r: r["Sorteo"], reverse=True)
    fieldnames = ["Juego", "Sorteo", "Fecha", "Números Ganadores"] + [f"Num_{i}" for i in range(1, 15)]
    save_excel_dual("resultados_kino", records, fieldnames, "Resultados Kino")

    # 2. Ejecutar motores KINO (Métodos 1, 2 y 3)
    sys.path.insert(0, os.path.join(BASE_DIR, "motores"))
    import kino_engine_metodo1, kino_engine_metodo2, kino_engine_metodo3
    print("Corriendo KINO Método 1...")
    kino_engine_metodo1.main()
    print("Corriendo KINO Método 2...")
    kino_engine_metodo2.main()
    print("Corriendo KINO Método 3...")
    kino_engine_metodo3.main()

    # 3. Recompilar JS con todos los métodos
    recompile_audit_js()

    kino_csv = os.path.join(AUDIT_DIR, "historial_walkforward_kino.csv")
    with open(kino_csv, 'r', encoding='utf-8') as f:
        audit_rows = list(csv.DictReader(f))

    latest_draw = records[0] if records else {}
    return {
        "success": True,
        "juego": "KINO",
        "total_sorteos_validos": len(records),
        "total_auditados": len(audit_rows),
        "ultimo_sorteo": str(latest_draw.get("Sorteo", "")),
        "fecha_ultimo_sorteo": latest_draw.get("Fecha", ""),
        "numeros_ganadores": latest_draw.get("Números Ganadores", ""),
        "tiempo_segundos": round(time.time() - t0, 1)
    }

if __name__ == "__main__":
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "all"
    if arg in ["loto", "all"]:
        print(">>> Actualizando LOTO...")
        res_loto = actualizar_loto()
        print("LOTO OK:", res_loto)
    if arg in ["kino", "all"]:
        print(">>> Actualizando KINO...")
        res_kino = actualizar_kino()
        print("KINO OK:", res_kino)
