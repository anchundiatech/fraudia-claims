# **Fraudia Claims** — Detector Inteligente de Fraudes en Siniestros

![Vercel](https://img.shields.io/badge/deploy-vercel-black?style=flat-square&logo=vercel)
![Next.js](https://img.shields.io/badge/frontend-Next.js%2015-blue?style=flat-square&logo=nextdotjs)
![FastAPI](https://img.shields.io/badge/backend-FastAPI-green?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/python-3.12-blue?style=flat-square)
![Claude](https://img.shields.io/badge/agent-Claude%203.5-orange?style=flat-square)

**Prototipo desarrollado para el hackIAthon 2026 — Reto Aseguradora del Sur**

Sistema inteligente que combina **motor de reglas de negocio** + **Inteligencia Artificial** para detectar y priorizar posibles fraudes en siniestros de seguros.

> **Principio de Auditoría Responsable:** Este sistema genera alertas de revisión y priorización. **Nunca** realiza acusaciones automáticas de fraude. Toda decisión final requiere revisión humana por un analista especializado.

---

## ✨ Características Principales

- Motor de reglas determinista con **14 señales de riesgo** ponderadas
- **4 reglas críticas** de override automático
- Agente IA conversacional (Claude 3.5) para auditoría y explicabilidad
- Detección de clonación de narrativas mediante **NLP** (TF-IDF + similitud coseno)
- Sistema de semáforo de riesgo (Verde / Amarillo / Rojo)
- Dashboard moderno y reactivo para analistas
- Exportación de casos priorizados en CSV
- 100% datos sintéticos (sin información personal real)

---

## 🛠️ Stack Tecnológico

| Capa              | Tecnología                          | Propósito |
|-------------------|-------------------------------------|---------|
| **Frontend**      | Next.js 15 + React 19 + Tailwind CSS | Dashboard interactivo |
| **Backend**       | FastAPI + Python 3.12               | API de alto rendimiento |
| **Motor de Reglas** | Python (reglas personalizadas)     | Evaluación determinista |
| **Inteligencia Artificial** | Claude 3.5 (Anthropic)         | Análisis y explicabilidad |
| **NLP**           | scikit-learn (TF-IDF)               | Detección de duplicidad |
| **Base de Datos** | Supabase (PostgreSQL)               | Almacenamiento en la nube |

---

## 📊 Motor de Detección de Riesgos

### Señales de Riesgo (14 señales ponderadas)
El sistema calcula un **score de 0 a 100** según las siguientes señales:

- **S01** Cercanía a vigencia de póliza
- **S02** Demora en denuncia de robo
- **S03/S04/S05** Frecuencia de siniestros (asegurado, vehículo, conductor)
- **S07** Proveedores o beneficiarios recurrentes
- **S11** Alteración o inconsistencia documental
- **S13** Duplicidad de narrativas (NLP)
- **S09** Dinámica inconsistente del evento
- ... y más

### Reglas Críticas (Override)
La activación de cualquiera de estas reglas fuerza el caso a **Rojo (mínimo 76 puntos)**:

- **RF01** Pérdida Total por Robo en circunstancias dudosas
- **RF02** Evidencia de falsificación o adulteración documental
- **RF03** Asegurado, beneficiario o proveedor en lista restrictiva
- **RF04** Dinámica del accidente físicamente imposible

---

## 🚦 Clasificación de Riesgo

| Score       | Semáforo       | Acción Recomendada                        |
|-------------|----------------|-------------------------------------------|
| 0 – 40      | **🟢 Verde**   | Aprobación express                        |
| 41 – 75     | **🟡 Amarillo**| Escalamiento a Unidad Antifraude          |
| 76 – 100    | **🔴 Rojo**    | Auditoría de campo prioritaria            |

---

## 🚀 Instalación y Ejecución Local

### Prerrequisitos
- Python 3.12+
- Node.js 18+ y pnpm (o npm)
- Cuenta en Supabase
- API Key de Claude 3.5 (o Grok / Gemini)

### 1. Clonar el repositorio
```bash
git clone https://github.com/anchundiatech/fraudia-claims.git
cd fraudia-claims
```

### 2. Backend (FastAPI)

```bash
cd src/app
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

pip install -r ../../requirements.txt

cp ../../.env.example ../../.env 
# Configura tus API keys en .env

python src/database/cargar_datos.py

uvicorn src.app.main:app --reload --port 8000
```

### 3. Frontend (Next.js)

```bash
cd frontend
cp .env.local.example .env.local
pnpm install
pnpm run dev
```

Dashboard disponible en: **http://localhost:3000**

---

## 🌐 Despliegue en Frontend Vercel 

```bash
vercel
vercel --prod
```

Configura las variables de entorno en Vercel:
- `ANTHROPIC_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

---

## 📁 Estructura del Proyecto

```bash
fraudia-claims/
├── frontend/              # Aplicación Next.js
├── src/
│   ├── app/               # FastAPI
│   ├── rules/             # Motor de reglas
│   ├── ai_agent/          # Agente IA
│   ├── database/          # Conexión Supabase
│   └── ingestion/         # Pipelines de datos
├── data/synthetic/        # Dataset sintético
├── tests/
└── docs/
```

---

## ⚖️ Ética y Responsabilidad

- Solo utiliza **datos sintéticos** (cumple con GDPR y leyes de protección de datos)
- Diseño **Human-in-the-loop**: el sistema apoya, no decide
- Transparencia total en el cálculo de scores
- Enfocado en minimizar impacto por falsos positivos

---

---

|Miembro equipo | LINKEDINK |
|-------------|----------------|
| ALEJNADRO ANCHUNDIA     | [CONECTAR](https://www.linkedin.com/in/alejandro-anchundia)   | 
| William Salazar     | [CONECTAR](https://www.linkedin.com/in/salazarwilliam)|
| Alicia Hurtado    | [CONECTAR](www.linkedin.com/in/alicia-hurtado-78baa6256)     | 

---

**Desarrollado con ❤️ para hackIAthon 2026**
