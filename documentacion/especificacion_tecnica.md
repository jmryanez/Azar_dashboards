# ESPECIFICACIÓN TÉCNICA Y MATEMÁTICA: LOTO (6/41) Y KINO (14/25)
## Documentación de Métodos Científicos, Arquitectura de Datos y Calendario de Sorteos

---

### 1. Resumen y Principios Científicos
Este proyecto implementa un sistema analítico determinista e inmutable para los juegos de azar chilenos **Loto** (Polla Chilena de Beneficencia) y **Kino** (Lotería de Concepción).

#### 1.1. Macroestados Combinatorios y Filtrado de Patologías
Aunque cada combinación individual tiene idéntica probabilidad matemática de extracción:
- $\mathbb{P}(\text{Loto}) = 1 / \binom{41}{6} = 1 / 4.496.388 \approx 2,22 \times 10^{-7}$
- $\mathbb{P}(\text{Kino}) = 1 / \binom{25}{14} = 1 / 4.457.400 \approx 2,24 \times 10^{-7}$

La distribución de los **macroestados** (propiedades agregadas como paridad, rangos de suma aritmética, espaciamiento y memoria de arrastre) sigue leyes hipergeométricas y normales. Apostar fuera de los macroestados centrales equivale a jugar combinaciones patológicas (ej. 6 pares o sumas extremas) que representan menos del 1% del histórico acumulado.

---

### 2. Especificación Analítica: LOTO (6 de 41) - Baja Densidad (14,6%)
1. **Balance de Paridad (Hipergeométrica)**:
   - Universo: 20 números pares $\{2, 4, \dots, 40\}$ y 21 impares $\{1, 3, \dots, 41\}$.
   - **3P - 3I**: 33,72% de los casos (óptimo primario).
   - **2P - 4I** y **4P - 2I**: 25,29% y 22,63% respectivamente.
   - En conjunto, estos 3 patrones cubren el **81,64% de todos los sorteos**.
2. **Co-ocurrencias y Lift (Apriori)**:
   $$\text{Lift}(A \to B) = \frac{\mathbb{P}(A \cap B)}{\mathbb{P}(A) \cdot \mathbb{P}(B)}$$
   Permite detectar pares y tríos que se atraen mutuamente por encima de la esperanza matemática sin sesgo de frecuencia base.
3. **Estadística de Orden Posicional $X_{(k)}$**:
   $$\mathbb{E}[X_{(k)}] = k \cdot \frac{N + 1}{n + 1} = 6 \cdot k$$
   - $X_{(1)} \in [1, 12]$ (media 6,0), $X_{(6)} \in [30, 41]$ (media 36,0). Corrige aglomeraciones antinaturales en el centro del cartón.
4. **Rango de Suma Aritmética**: Media $\mu = 126,0$, $\sigma = 24,5$. Intervalo de confianza: **[100, 155]**.

---

### 3. Especificación Analítica: KINO (14 de 25) - Alta Densidad (56,0%)
1. **Ingeniería Inversa: Los 11 Ausentes**:
   - Modelado dual del cartón mediante el complemento $S^c = \{1 \dots 25\} \setminus S$.
   - Detección de duplas y tríos que suelen quedarse fuera juntos con frecuencia superior al azar ($\approx 18,3\%$).
2. **Matriz de Repulsión (Coeficiente $\phi$ de Pearson)**:
   - Evalúa inhibición estadística mutua entre pares de números. Si $\phi < -0,10$, los números se repelen y no deben jugarse juntos.
3. **Memoria Temporal: Tasa de Arrastre (Overlap)**:
   - Número de bolitas repetidas del sorteo anterior $S_{t-1}$.
   - Esperanza matemática: $\mathbb{E} = \frac{14 \times 14}{25} = \mathbf{7,84 \text{ bolitas}}$.
   - En el **77,29% de los sorteos históricos**, el resultado repite exactamente **7, 8 o 9 bolitas** del sorteo previo.
4. **Balance de Paridad**: 12 pares y 13 impares. 7P-7I (33,6%) y 6P-8I (25,2%). Suma en **[165, 200]** ($\mu = 182,0$).

---

### 4. Calendario Oficial y Ciclo de Sorteos en Chile (Horario Continental UTC-3)

| Juego | Días Oficiales | Hora Extracción | Actualización Recomendada en Excel |
| :--- | :--- | :--- | :--- |
| **LOTO (6/41)** | **Martes, Jueves y Domingo** | **21:00 hrs** | Mismo día a partir de las **21:30 hrs** |
| **KINO (14/25)** | **Miércoles, Viernes y Domingo** | **22:30 hrs** | Mismo día a partir de las **23:00 hrs** |

---

### 5. Guía de Ejecución del Script Python (`loto_kino_engine.py`)

```bash
# 1. Instalar dependencias necesarias
pip install pandas openpyxl numpy scipy

# 2. Ejecutar análisis apuntando a tu archivo Excel
python3 loto_kino_engine.py --excel "sorteos_historicos.xlsx" --recs 5

# 3. Ejecutar solo para Loto o solo para Kino
python3 loto_kino_engine.py --excel "sorteos_historicos.xlsx" --juego loto
python3 loto_kino_engine.py --excel "sorteos_historicos.xlsx" --juego kino
```
