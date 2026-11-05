# Plataforma Cuantitativa y Predictiva: LOTO (6/41) & KINO (14/25) Chile

> **Arquitectura de Simulación Walk-Forward Paso a Paso, Autoaprendizaje Adaptativo Softmax y Visualización en DataTables**

Esta aplicación es una plataforma cuantitativa orientada al análisis matemático y predictivo de los dos sorteos de azar más tradicionales de Chile: **LOTO (6 de 41)** y **KINO (14 de 25)**. 

El sistema implementa dos motores matemáticos desacoplados para baja y alta densidad, auditados mediante una simulación histórica **Walk-Forward** sorteo por sorteo (sin fuga de datos o *look-ahead bias*) con autoaprendizaje continuo basado en regularización $L_2$ y normalización *Softmax*.

---

## 🚀 Despliegue Inmediato en GitHub Pages (1 Clic)

Esta plataforma está estructurada como una **Single Page Application (SPA) 100% estática**: no requiere servidores Node.js, Python o bases de datos en la nube para funcionar en la web.

Para activarla como página web pública en tu cuenta de GitHub:

1. Crea un nuevo repositorio en tu GitHub (por ejemplo, `azar-analytics-chile`).
2. Sube este proyecto con los comandos habituales:
   ```bash
   git remote add origin https://github.com/TU_USUARIO/azar-analytics-chile.git
   git push -u origin main
   ```
3. En tu repositorio en GitHub, ve a **Settings** > **Pages**.
4. En **Build and deployment** > **Branch**, selecciona `main` y carpeta `/ (root)`.
5. Haz clic en **Save**. En un minuto tendrás tu aplicación web activa en:
   `https://TU_USUARIO.github.io/azar-analytics-chile/`

---

## 📊 Características y Novedades de la Aplicación

1. **Integración con DataTables.net**:
   * Paginación dinámica (10, 25, 50, 100 registros por página).
   * Búsqueda en tiempo real por fecha, número de sorteo o combinaciones.
   * Ordenamiento multidireccional (puedes ordenar por la columna **Aciertos** de mayor a menor para ver inmediatamente todos los premios históricos obtenidos).
2. **Tarjetas Métricas Interactivas (Filtros con 1 Clic)**:
   * Al hacer clic en **3 Aciertos (Ternas)** o **4 Aciertos (Cuaternas)** en Loto, la tabla de DataTables se filtra al instante para mostrar únicamente esos sorteos.
   * En Kino, filtra con un solo clic los **11 Aciertos (Categoría Premiada Oficial)** o los **12 Aciertos (Premios Mayores)**.
3. **Métricas y Gráficos Estadísticos Reincorporados**:
   * **Frecuencias Absolutas de Bolitas**: visualización de 01 a 41 (Loto) y 01 a 25 (Kino) diferenciando pares e impares.
   * **Balance de Paridad**: contraste empírico observado vs. distribución hipergeométrica teórica.
   * **Cartón Físico 5x5 de Kino**: mapa de calor interactivo con las tasas porcentuales de presencia de cada casilla.
   * **Tasa de Arrastre Temporal**: curva empírica de solapamiento de bolitas respecto al sorteo previo ($E = 7,84$ bolitas).
   * **Series Temporales Walk-Forward**: evolución de aciertos en el tiempo con medias móviles.

---

## 🏗️ Estructura del Proyecto

```text
.
├── index.html                        # Aplicación web interactiva (GitHub Pages ready)
├── dashboard_loto_kino.html          # Copia espejo local de la aplicación
├── README.md                         # Documentación técnica completa
├── .gitignore                        # Exclusiones de archivos del sistema
│
├── datos/                            # Bases de datos históricas originales
│   ├── resultados_loto.xlsm          # Base oficial LOTO Chile
│   └── resultados_kino.xlsm          # Base oficial KINO Chile
│
├── auditoria_walkforward/            # Salidas auditables y memorias de autoaprendizaje
│   ├── auditoria_data.js             # Dataset JavaScript precargado (evita bloqueos CORS)
│   ├── historial_walkforward_loto.csv # 733 sorteos Loto auditados paso a paso
│   ├── historial_walkforward_kino.csv # 1.723 sorteos Kino auditados paso a paso
│   ├── loto_brain_state.json         # Pesos óptimos y estado del cerebro Loto
│   ├── kino_brain_state.json         # Pesos óptimos y estado del cerebro Kino
│   ├── propuestas_loto.txt           # Reporte ejecutivo Loto
│   └── propuestas_kino.txt           # Reporte ejecutivo Kino
│
├── motores/                          # Motores cuantitativos independientes en Python
│   ├── loto_engine.py                # Algoritmo especializado en baja densidad (6/41)
│   └── kino_engine.py                # Algoritmo especializado en alta densidad (14/25)
│
└── documentacion/                    # Especificaciones teóricas y memoria de cálculo
    └── especificacion_tecnica.md
```

---

## 🧮 Fundamentos Matemáticos Rigurosos

* **Lift Hipergeométrico con FDR Benjamini-Hochberg**: corrige el sesgo del algoritmo Apriori para muestreo finito sin reemplazo:
  $$\mathbb{P}(A \cap B)_{\text{esperada}} = \frac{k(k-1)}{N(N-1)}$$
* **Ingeniería Inversa de los 11 Ausentes**: optimización dual para alta densidad ($56,0\%$). Seleccionar 14 bolitas equivale a descartar el vector binario de 11 ausentes ($\sim \text{mask}$).
* **Matriz de Repulsión $\phi$ de Pearson con prueba $\chi^2$**: identifica duplas con inhibición mutua estadísticamente significativa ($p < 0,001$).
* **Varianza Beta-Binomial de Estadísticos de Orden**: bandas de dispersión asimétricas para las bolitas ordenadas $X_{(1)}$ a $X_{(6)}$.
* **Autoaprendizaje Softmax Bounded con $L_2$ Regularization**:
  $$w_i^{(t+1)} = \frac{\exp(z_i^{(t+1)})}{\sum_j \exp(z_j^{(t+1)})}, \quad z_i^{(t+1)} = (1 - \lambda) z_i^{(t)} + \eta \cdot (\text{Aciertos} - \mathbb{E}[\text{Aciertos}])$$

---

## 📅 Horarios Oficiales de Sorteos (Chile)

* **LOTO**: Martes, Jueves y Domingo a las 21:00 CLT.
* **KINO**: Miércoles, Viernes y Domingo a las 22:30 CLT.
