# 🔍 Fraudia Claims — Detector de Posibles Fraudes en Siniestros

> Prototipo funcional de IA para detección de posibles fraudes en siniestros de seguros.
> Desarrollado para el **hackIAthon 2026 — Reto Aseguradora del Sur**.

⚠️ **Principio clave:** Este sistema genera alertas de revisión, no acusaciones automáticas de fraude. Toda decisión final requiere revisión humana.

---

## 🏗️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Frontend | Next.js 14 + Tailwind CSS |
| Backend / API | Python 3.11 + FastAPI |
| Motor de reglas | Python (reglas ponderadas del reto) |
| Agente de IA | Claude API (Anthropic) |
| Análisis NLP | scikit-learn (TF-IDF similitud textual) |
| Datos | CSV sintético / SQLite |

---

## 🚀 Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/anchundiatech/fraudia-claims.git
cd fraudia-claims
```

### 2. Backend (Python + FastAPI)

```bash
cd src/app
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r ../../requirements.txt
cp ../../.env.example ../../.env   # Agrega tu ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000
```

API disponible en: http://localhost:8000
Docs interactivas: http://localhost:8000/docs

### 3. Frontend (Next.js)

```bash
cd frontend
pnpm install
cp .env.local.example .env.local
pnpm run dev
```

Dashboard disponible en: http://localhost:3000

---

## 📁 Estructura del repositorio

```
fraudia-claims/
├── README.md
├── requirements.txt          # Dependencias Python
├── .env.example              # Variables de entorno (sin credenciales)
├── data/
│   ├── raw/                  # Datos originales sin procesar
│   ├── processed/            # Datos procesados
│   └── synthetic/            # Dataset sintético generado
├── notebooks/
│   ├── 01_exploracion_datos.ipynb
│   ├── 02_modelo_fraude.ipynb
│   └── 03_evaluacion_modelo.ipynb
├── src/
│   ├── ingestion/            # Carga y validación de datos
│   ├── features/             # Ingeniería de variables
│   ├── rules/                # Motor de reglas de negocio
│   ├── models/               # Modelo ML de score
│   ├── explainability/       # Explicación del score
│   ├── ai_agent/             # Agente Claude para consultas
│   └── app/                  # FastAPI — entry point
├── frontend/                 # Next.js dashboard
├── docs/
│   ├── arquitectura.md
│   ├── modelo_datos.md
│   ├── reglas_negocio.md
│   ├── uso_ia.md
│   └── limitaciones.md
├── tests/
│   └── test_rules.py
└── presentation/
    └── pitch.pdf
```

---

## 🎯 Funcionalidades

- ✅ Carga y validación de dataset de siniestros
- ✅ Motor de 12 señales de riesgo con puntuación ponderada
- ✅ Score de posible fraude (0–100) con semáforo 🟢🟡🔴
- ✅ Dashboard interactivo con tabla de casos priorizados
- ✅ Vista de detalle con explicación de alertas activadas
- ✅ Agente de IA para consultas en lenguaje natural
- ✅ Análisis NLP de similitud entre narrativas
- ✅ Exportación de reporte de casos sospechosos

---

## 📊 Score de riesgo

| Rango | Nivel | Acción |
|---|---|---|
| 0 – 40 | 🟢 Verde (Bajo) | Continuar flujo normal |
| 41 – 75 | 🟡 Amarillo (Medio) | Escalar a Unidad Antifraude |
| 76 – 100 | 🔴 Rojo (Alto) | Revisión especializada de campo |

---

## ⚖️ Ética y limitaciones

- Los datos usados son 100% sintéticos, no contienen información personal real.
- El sistema **no acusa** ni **rechaza** siniestros automáticamente.
- Los resultados son alertas para revisión humana especializada.
- El modelo puede generar falsos positivos — ver `docs/limitaciones.md`.

---

## 👥 Equipo

hackIAthon 2026 — Reto Aseguradora del Sur
