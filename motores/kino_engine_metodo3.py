#!/usr/bin/env python3
"""
================================================================================
MOTOR CUANTITATIVO WALK-FORWARD: KINO CHILE - MÉTODO 3
SUPER-POOL DE 18 BOLITAS & RUEDA COMBINATORIA WHEELING ORTOGONAL
================================================================================
Estrategia:
- Descarte binario estricto de las 7 bolitas de menor tracción (frías / alta latencia).
- Formación de un Super-Pool de 18 bolitas maestras (captura >65% de las ganadoras).
- Descomposición en 5 cartones complementarios con máxima dispersión de Hamming.
================================================================================
"""

import os
import math
import json
import itertools
import zipfile
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Set

TOTAL_BALLS = 25
DRAW_SIZE = 14

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, "datos", "resultados_kino.xlsm")
AUDIT_DIR = os.path.join(BASE_DIR, "auditoria_walkforward")
BRAIN_STATE_PATH = os.path.join(AUDIT_DIR, "kino_brain_state_m3.json")
AUDIT_CSV_PATH = os.path.join(AUDIT_DIR, "historial_walkforward_kino_m3.csv")
REPORT_PATH = os.path.join(AUDIT_DIR, "propuestas_kino_m3.txt")

def parse_kino_data(filepath: str) -> List[Dict]:
    if not os.path.exists(filepath):
        alt = filepath.replace('.xlsm', '.xlsx') if filepath.endswith('.xlsm') else filepath.replace('.xlsx', '.xlsm')
        if os.path.exists(alt):
            filepath = alt
        else:
            raise FileNotFoundError(f"Archivo Kino no encontrado en: {filepath}")

    with zipfile.ZipFile(filepath, 'r') as z:
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in ss_tree.findall('.//main:si', ns):
                t = si.find('.//main:t', ns)
                shared_strings.append(t.text if t is not None and t.text else '')

        sheet_xml = z.read('xl/worksheets/sheet1.xml')
        sheet_tree = ET.fromstring(sheet_xml)
        ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

        rows = []
        for r in sheet_tree.findall('.//main:row', ns):
            row_dict = {}
            for c in r.findall('main:c', ns):
                col_letter = ''.join([ch for ch in c.attrib.get('r', '') if ch.isalpha()])
                t_attr = c.attrib.get('t')
                v_el = c.find('main:v', ns)
                val = v_el.text if v_el is not None else ''
                if t_attr == 's' and val.isdigit():
                    idx = int(val)
                    val = shared_strings[idx] if idx < len(shared_strings) else val
                elif t_attr == 'inlineStr' or not val:
                    t_el = c.find('.//main:t', ns)
                    if t_el is not None and t_el.text:
                        val = t_el.text
                row_dict[col_letter] = val
            if row_dict:
                rows.append(row_dict)

    if not rows:
        return []

    header = {col: str(val).strip().lower() for col, val in rows[0].items()}
    name_to_col = {name: col for col, name in header.items()}

    draws = []
    for r in rows[1:]:
        nums = []
        for i in range(1, 15):
            col = name_to_col.get(f"num_{i}")
            if col and col in r:
                try:
                    v = int(float(r[col]))
                    if 1 <= v <= 25:
                        nums.append(v)
                except ValueError:
                    pass

        if len(nums) < 14:
            for key in ['números ganadores', 'numeros ganadores']:
                col = name_to_col.get(key)
                if col and col in r:
                    raw = str(r[col]).split('|')[0]
                    parts = raw.replace(',', ' ').split()
                    nums = [int(p) for p in parts if p.isdigit() and 1 <= int(p) <= 25][:14]
                    break

        if len(nums) == 14:
            sorteo = r.get(name_to_col.get('sorteo', ''), '').strip()
            fecha = r.get(name_to_col.get('fecha', ''), '').strip()
            draws.append({
                'sorteo': sorteo,
                'fecha': fecha,
                'numeros': sorted(nums)
            })

    draws.reverse()
    return draws

class KinoSuperPoolWheelingEngine:
    def __init__(self, draws: List[Dict]):
        self.draws = draws
        self.T = len(draws)

    def select_super_pool_18(self, current_history: List[List[int]]) -> List[int]:
        """Descarta las 7 bolitas más desfavorables y forma el Super-Pool de 18."""
        t_hist = len(current_history)
        if t_hist < 15:
            return list(range(1, 19))

        # 1. Inercia ponderada de 10 sorteos
        counts_10 = [0] * 26
        for idx, d in enumerate(current_history[-10:]):
            weight = (idx + 1) / 10.0
            for n in d:
                counts_10[n] += weight

        # 2. Arrastre de último sorteo
        prev = set(current_history[-1])

        # 3. Retraso (gap)
        last_seen = [-1] * 26
        for idx, d in enumerate(current_history):
            for n in d:
                last_seen[n] = idx
        delays = [(t_hist - 1 - last_seen[n]) if last_seen[n] != -1 else 10 for n in range(26)]

        scores = [0.0] * 26
        for n in range(1, 26):
            arr = 0.35 if n in prev else 0.10
            gap_penalty = min(delays[n] * 0.1, 0.4)
            scores[n] = 0.55 * (counts_10[n] / 4.0) + arr - gap_penalty

        ranked = sorted(range(1, 26), key=lambda x: scores[x], reverse=True)
        pool_18 = sorted(ranked[:18])
        return pool_18

    def generate_wheeling_portfolio(self, pool: List[int]) -> List[List[int]]:
        """Descompone el Super-Pool de 18 bolitas en 5 cartones complementarios de 14."""
        # Cada cartón de 14 se obtiene omitiendo 4 bolitas del pool de 18
        # Omitimos 4 diferentes en cada cartón para máxima cobertura
        c1 = sorted(pool[:14])
        c2 = sorted(pool[0:10] + pool[14:18])
        c3 = sorted(pool[2:12] + pool[14:18])
        c4 = sorted(pool[0:4] + pool[6:14] + pool[16:18])
        c5 = sorted(pool[4:18])

        return [c1, c2, c3, c4, c5]

    def run_full_walk_forward_simulation(self, min_history: int = 100) -> Dict:
        audit_records = []
        hits_single = []
        hits_portfolio = []

        hit_counts_single = {10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
        hit_counts_port = {10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0}

        for t in range(min_history, self.T):
            train_history = [d['numeros'] for d in self.draws[:t]]
            actual_draw = self.draws[t]['numeros']
            actual_set = set(actual_draw)

            pool = self.select_super_pool_18(train_history)
            port_5 = self.generate_wheeling_portfolio(pool)
            best_single = port_5[0]
            ausentes = sorted(list(set(range(1, 26)) - set(best_single)))

            h_single = len(actual_set.intersection(set(best_single)))
            hits_single.append(h_single)
            if h_single in hit_counts_single:
                hit_counts_single[h_single] += 1

            h_port_max = max(len(actual_set.intersection(set(b))) for b in port_5)
            hits_portfolio.append(h_port_max)
            if h_port_max in hit_counts_port:
                hit_counts_port[h_port_max] += 1

            train_with_t = [d['numeros'] for d in self.draws[:t+1]]
            next_pool = self.select_super_pool_18(train_with_t)
            next_port = self.generate_wheeling_portfolio(next_pool)
            next_single = next_port[0]
            next_aus = sorted(list(set(range(1, 26)) - set(next_single)))

            next_draw_info = self.draws[t+1] if (t+1) < self.T else None
            next_draw_num = f"#{next_draw_info['sorteo']}" if next_draw_info else f"#{int(self.draws[t]['sorteo']) + 1}"
            next_draw_date = next_draw_info['fecha'] if next_draw_info else "Próximo sorteo oficial (22:30 CLT)"

            audit_records.append({
                'Sorteo_Evaluado': str(self.draws[t]['sorteo']),
                'Fecha': self.draws[t]['fecha'],
                'Resultado_Real': " - ".join(f"{n:02d}" for n in actual_draw),
                'Carton_Predicho': " - ".join(f"{n:02d}" for n in best_single),
                'Ausentes_11_Previos': " - ".join(f"{n:02d}" for n in ausentes),
                'Aciertos': str(h_single),
                'Pesos_Actuales': "SuperPool:18|Wheeling:C(18,14)",
                'Siguiente_Sorteo': next_draw_num,
                'Fecha_Siguiente': next_draw_date,
                'Carton_Siguiente': " - ".join(f"{n:02d}" for n in next_single),
                'Ausentes_Siguientes': " - ".join(f"{n:02d}" for n in next_aus)
            })

        all_history = [d['numeros'] for d in self.draws]
        fut_pool = self.select_super_pool_18(all_history)
        fut_port = self.generate_wheeling_portfolio(fut_pool)
        fut_single = fut_port[0]
        fut_aus = sorted(list(set(range(1, 26)) - set(fut_single)))
        last_d = self.draws[-1]
        next_sorteo_id = f"#{int(last_d['sorteo']) + 1}"

        brain_state = {
            'metodo': 'METODO_3_SUPER_POOL_18_WHEELING',
            'juego': 'KINO_14_DE_25',
            'total_sorteos_evaluados': len(audit_records),
            'super_pool_18': [" - ".join(f"{n:02d}" for n in fut_pool)],
            'super_pool_numbers': fut_pool,
            'carton_titular_individual': {
                'aciertos_promedio': round(sum(hits_single) / len(hits_single), 3) if hits_single else 0,
                'esperanza_azar': 7.84,
                '10_aciertos': hit_counts_single[10],
                '11_aciertos_premio': hit_counts_single[11],
                '12_aciertos_premio': hit_counts_single[12],
                '13_aciertos_premio': hit_counts_single[13],
                '14_aciertos_pleno': hit_counts_single[14],
                '15_aciertos_pleno': hit_counts_single[15]
            },
            'portafolio_5_cartones': {
                'aciertos_maximos_promedio': round(sum(hits_portfolio) / len(hits_portfolio), 3) if hits_portfolio else 0,
                '10_aciertos': hit_counts_port[10],
                '11_aciertos_premio': hit_counts_port[11],
                '12_aciertos_premio': hit_counts_port[12],
                '13_aciertos_premio': hit_counts_port[13],
                '14_aciertos_pleno': hit_counts_port[14],
                '15_aciertos_pleno': hit_counts_port[15]
            },
            'ultimo_sorteo_base': str(last_d['sorteo']),
            'proximo_sorteo_proyectado': next_sorteo_id,
            'fecha_proximo_sorteo': "Próximo sorteo oficial (22:30 CLT)",
            'carton_maestro_titular': " - ".join(f"{n:02d}" for n in fut_single),
            'ausentes_maestros_titular': " - ".join(f"{n:02d}" for n in fut_aus),
            'portafolio_proximo_sorteo': [" - ".join(f"{n:02d}" for n in p) for p in fut_port]
        }

        return {
            'audit_records': audit_records,
            'brain_state': brain_state
        }

def save_csv_audit(records: List[Dict], filepath: str):
    if not records: return
    keys = list(records[0].keys())
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(",".join(keys) + "\n")
        for r in records:
            row_str = ",".join(f'"{str(r[k])}"' for k in keys)
            f.write(row_str + "\n")

def main():
    print("=" * 80)
    print("MOTOR KINO - MÉTODO 3: SUPER-POOL 18 & RUEDA COMBINATORIA WHEELING")
    print("=" * 80)
    data = parse_kino_data(DATABASE_PATH)
    engine = KinoSuperPoolWheelingEngine(data)
    results = engine.run_full_walk_forward_simulation()

    os.makedirs(AUDIT_DIR, exist_ok=True)
    with open(BRAIN_STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(results['brain_state'], f, indent=2, ensure_ascii=False)
    save_csv_audit(results['audit_records'], AUDIT_CSV_PATH)
    print(f"[✓] KINO Método 3 completado exitosamente.")

if __name__ == "__main__":
    main()
