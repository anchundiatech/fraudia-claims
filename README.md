# Fraudia Claims — Detector de Posibles Fraudes en Siniestros

[Vercel Deployment](https://img.shields.io/badge/deploy-vercel-black?style=flat-square&logo=vercel)
[Next.js](https://img.shields.io/badge/frontend-Next.js%2015-blue?style=flat-square&logo=nextdotjs)
[FastAPI](https://img.shields.io/badge/backend-FastAPI-green?style=flat-square&logo=fastapi)
[Python](https://img.shields.io/badge/python-3.12-blue?style=flat-square)
[Claude API](https://img.shields.io/badge/agent-Claude%203.5-orange?style=flat-square)

Prototipo funcional de Inteligencia Artificial y motor de reglas de negocio para la detección y auditoría de posibles fraudes en siniestros de seguros, desarrollado para el **hackIAthon 2026 — Reto Aseguradora del Sur**.

> **Principio de Auditoría Responsable:** Este sistema genera alertas de revisión técnica y priorización de cartera, no acusaciones automáticas de fraude. Toda decisión final requiere la intervención y revisión humana de un analista especializado.

---

## Stack Tecnológico

| Capa | Tecnología | Descripción |
|---|---|---|
| **Frontend** | Next.js 15 + React 19 + Tailwind CSS | Interfaz moderna, reactiva y optimizada para la visualización de analistas. |
| **Backend / API** | Python 3.12 + FastAPI | API de alta velocidad, auto-documentada, y estructurada para auditorías. |
| **Motor de Reglas** | Python (14 Señales + 4 Reglas Críticas) | Motor determinista y transparente basado en el pliego de condiciones. |
| **Agente de IA** | Claude 3.5 API (Anthropic) | Agente auditor conversacional entrenado para análisis de casos y explicabilidad. |
| **Análisis NLP** | scikit-learn (TF-IDF Cosine Similarity) | Algoritmo de similitud textual para identificar duplicidad de narrativas (clonación). |
| **Datos** | CSV Sintético / SQLite | Repositorio local estructurado libre de información personal real (PII). |

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Usuario (Analista)                   │
└────────────────────────────┬────────────────────────────┘
                             │ Navegador
┌────────────────────────────▼────────────────────────────┐
│              Frontend — Next.js 15 (Puerto 3000)        │
│   Dashboard · Tabla de Siniestros · Audit IA · Métricas │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP REST API
┌────────────────────────────▼────────────────────────────┐
│              Backend — Python FastAPI (Puerto 8000)     │
│                                                         │
│   /siniestros      → Lista con puntaje unificado        │
│   /siniestros/:id  → Detalle interactivo y alertas     │
│   /estadisticas    → KPIs consolidados del dashboard    │
│   /chat            → Agente Audit IA (Claude API)       │
│   /exportar/csv    → Exportación de casos priorizados  │
│                                                         │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │ Motor Reglas │  │ NLP Similitud│  │ Claude API   │  │
│   │ (14 señales) │  │ (TF-IDF)     │  │ (Audit IA)   │  │
│   └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────────┬────────────────────────────┘
                             │ Acceso a Datos
┌────────────────────────────▼────────────────────────────┐
│           Dataset Unificado (CSV / SQLite)              │
│   siniestros · pólizas · asegurados · proveedores       │
└─────────────────────────────────────────────────────────┘
```

---

## Motor de Detección de Riesgos

El núcleo del backend ejecuta una evaluación detallada basada en **14 señales de riesgo ponderadas** y **4 reglas críticas de descarte inmediato (Overrides)**, arrojando una puntuación de **0 a 100**.

### 1. Señales de Riesgo Ponderadas

| Código | Señal de Alerta | Severidad / Puntos | Condición de Activación |
|---|---|---|---|
| **S01** | Cercanía a vigencia de póliza | Alta (8 pts) / Media (4 pts) | Siniestro en ≤10 días del inicio (8 pts) o 11–30 días (4 pts). |
| **S02** | Demora en denuncia de robo | Alta (8 pts) / Media (4 pts) | Denuncia realizada >48 horas del evento (8 pts) o 24–48 horas (4 pts). |
| **S03** | Frecuencia de siniestros - Asegurado | Alta (8 pts) / Media (4 pts) | Asegurado con ≥3 siniestros previos en ≤18 meses (8 pts) o 2 siniestros (4 pts). |
| **S04** | Frecuencia de siniestros - Vehículo | Alta (6 pts) / Media (3 pts) | Vehículo involucrado en ≥3 siniestros en ≤18 meses (6 pts) o 2 (3 pts). |
| **S05** | Frecuencia de siniestros - Conductor | Alta (8 pts) / Media (4 pts) | Conductor registrado en ≥3 siniestros en ≤18 meses (8 pts) o 2 (4 pts). |
| **S06** | Alta frecuencia de eventos de solo RC | Media (6 pts) / Baja (3 pts) | Asegurado con >2 siniestros exclusivos de RC (6 pts) o 1 previo (3 pts). |
| **S07** | Proveedor o Beneficiario recurrente | Alta (10 pts) / Media (5 pts) | Proveedor en lista restrictiva (10 pts) o con >2 casos observados al año (5 pts). |
| **S08** | Documentación obligatoria incompleta | Media (4 pts) | Falta de entrega de requisitos legales exigibles. |
| **S09** | Dinámica o relato inconsistente | Alta (6 pts) / Media (3 pts) | Relato inconsistente con el daño (6 pts) o colisión múltiple de madrugada (3 pts). |
| **S10** | Eventos sin tercero identificado | Media (5 pts) | Daño de severidad alta reportado sin datos de un tercero ni cámaras. |
| **S11** | Alteración o inconsistencia documental | Alta (10 pts) | Documentación presentada con fechas falsificadas o importes alterados. |
| **S12** | Reporte tardío general | Media (5 pts) / Baja (3 pts) | Reporte tardío del siniestro >7 días (5 pts) o entre 4–7 días (3 pts). |
| **S13** | Duplicidad o similitud de narrativas (NLP) | Alta (8 pts) / Media (4 pts) | Coincidencia de relatos por algoritmo TF-IDF >85% (8 pts) o 70–85% (4 pts). |
| **S14** | Reclamación cercana a suma asegurada | Media (4 pts) | Importe reclamado representa ≥95% del límite de cobertura total. |

### 2. Reglas Críticas (Override de Puntuación)

La activación de cualquiera de las siguientes condiciones fuerza el score del caso directamente al rango **ROJO (mínimo de 76 puntos)** para su investigación de campo prioritaria por parte de la Unidad Antifraude:

*   **RF01**: Cobertura de Pérdida Total por Robo (PTxRB) en circunstancias dudosas.
*   **RF02**: Evidencia física o pericial de falsificación o adulteración documental directa.
*   **RF03**: Asegurado, beneficiario o taller proveedor listado activamente en Lista Restrictiva de la compañía.
*   **RF04**: Dinámica declarada del accidente catalogada como físicamente imposible por reconstructores.

---

## Clasificación del Semáforo de Riesgo

| Rango de Score | Nivel de Riesgo | Acción Sugerida |
|---|---|---|
| **0 – 40** | Verde (Bajo) | **Aprobación Express:** Continuar con el flujo normal de pago del siniestro. |
| **41 – 75** | Amarillo (Medio) | **Escalamiento:** Derivar a la Unidad Antifraude para análisis documental y llamadas. |
| **76 – 100** | Rojo (Alto / Crítico) | **Auditoría de Campo:** Inspección física, revisión pericial y suspensión del pago de inmediato. |

---

## Instalación y Ejecución Local

### 1. Requisitos Previos

*   Python 3.12+ instalado.
*   Node.js 18+ y `pnpm` o `npm` instalado.
*   Una cuenta y un proyecto creado en **Supabase** (para el almacenamiento de los datos) y/o tu API Key de tu proveedor de IA de preferencia (**xAI (Grok)**, **Gemini** o **Anthropic (Claude)**).

### 2. Clonar el repositorio

```bash
git clone https://github.com/anchundiatech/fraudia-claims.git
cd fraudia-claims
```

### 3. Servidor Backend (FastAPI)

Sigue estos pasos detallados desde la raíz del proyecto para inicializar el entorno, configurar la base de datos y arrancar la API local:

#### Paso 3.1: Entorno Virtual y Dependencias
1. Crea y activa tu entorno virtual de Python:
   ```bash
   python -m venv venv
   # En Windows (Git Bash):
   source venv/Scripts/activate
   # En Windows (cmd.exe):
   venv\Scripts\activate
   # En macOS/Linux:
   source venv/bin/activate
   ```
2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

#### Paso 3.2: Variables de Entorno (.env)
1. Copia la plantilla de variables de entorno a tu archivo local:
   ```bash
   cp .env.example .env
   ```
2. Abre el archivo `.env` en tu editor y configura tus claves:
   *   **Para el Agente de IA**: Define `AI_PROVIDER` (`xai`, `gemini` o `anthropic`) y agrega su respectiva API key (`XAI_API_KEY`, `GEMINI_API_KEY` o `ANTHROPIC_API_KEY`).
   *   **Para la Base de Datos (Supabase)**: Agrega tus claves de conexión de Supabase en `SUPABASE_URL` y `SUPABASE_KEY` (puedes obtenerlas en el panel de configuración de tu proyecto de Supabase en API -> Project API Keys).

#### Paso 3.3: Sembrado de Datos (Seeding a Supabase)
> **CRÍTICO:** Es obligatorio cargar tus datos en tu instancia de Supabase antes de iniciar el servidor por primera vez para que las tablas de siniestros, pólizas, documentos y clasificaciones se creen y se pueblen con los datos sintéticos.

1. Ejecuta el script de carga desde la raíz del proyecto:
   ```bash
   python src/database/cargar_datos.py
   ```
   *Este script leerá automáticamente el dataset sintético localizado en `data/synthetic/siniestros.csv` y lo subirá a las tablas correspondientes en tu nube de Supabase.*

#### Paso 3.4: Iniciar el Servidor API
1. Arranca el servidor FastAPI de desarrollo:
   ```bash
   uvicorn src.app.main:app --reload --port 8000
   ```
   *   API Local activa en: `http://localhost:8000`
   *   Swagger UI (Documentación interactiva y pruebas de endpoints): `http://localhost:8000/docs`

### 4. Cliente Frontend (Next.js)

Abre otra terminal diferente y ejecuta los siguientes comandos para iniciar la interfaz gráfica del Dashboard:

1. Dirígete a la carpeta `frontend`:
   ```bash
   cd frontend
   ```
2. Instala las dependencias del paquete:
   ```bash
   pnpm install
   # O si usas npm:
   npm install
   ```
3. Configura el entorno del frontend:
   ```bash
   cp .env.local.example .env.local
   ```
4. Ejecuta el servidor Next.js en modo de desarrollo:
   ```bash
   pnpm run dev
   # O si usas npm:
   npm run dev
   ```
   *   Dashboard del analista activo en: `http://localhost:3000`

---

## Guía de Despliegue en Vercel

Este repositorio está configurado para desplegarse fácilmente tanto en la interfaz web como en el backend API utilizando la infraestructura serverless de **Vercel**.

### Configuración de Archivos para Vercel
*   `pyproject.toml`: Define el proyecto de backend y le indica a Vercel el punto de entrada de la aplicación FastAPI.
*   `vercel.json`: Configura la ejecución del runtime serverless para Python (`vercel-python@0.7.3`) que procesará las solicitudes a la API.

### Despliegue Paso a Paso

1. Instala la herramienta CLI de Vercel si aún no la tienes:
   ```bash
   npm install -g vercel
   ```
2. Desde la raíz del repositorio, vincula tu cuenta y crea el despliegue del proyecto:
   ```bash
   vercel
   ```
3. Configura las siguientes variables de entorno en el panel de control de tu proyecto en Vercel:
   *   `ANTHROPIC_API_KEY`: Tu clave de API de Anthropic Claude para el agente de auditoría conversacional.
   *   `DB_TABLE_SINIESTROS` (Opcional): Nombre de la vista de datos de auditoría de Supabase (por defecto `vPoliza_Puntaje_Total`).
   *   `SUPABASE_URL` / `SUPABASE_KEY` (Opcional): Si deseas conectarte a una instancia cloud de Supabase en producción.

4. Para enviar tu código final a producción, ejecuta:
   ```bash
   vercel --prod
   ```

---

## 📁 Estructura del Repositorio

```
fraudia-claims/
├── README.md                 # Guía general e información del proyecto
├── pyproject.toml            # Configuración de empaquetado y entrypoint Vercel
├── vercel.json               # Configuración del runtime serverless de Vercel
├── requirements.txt          # Dependencias de Python Backend
├── .env.example              # Plantilla de variables de entorno
├── data/
│   ├── raw/                  # Datos de siniestros crudos
│   ├── processed/            # Datos transformados y filtrados
│   └── synthetic/            # Dataset sintético de simulación
├── frontend/                 # Aplicación Next.js 15 (React 19, Tailwind)
│   ├── src/
│   │   ├── app/              # Rutas, Layout y Dashboard de usuario
│   │   └── lib/              # Integración API y cálculo de semáforo
│   ├── package.json          # Dependencias de NodeJS
│   └── tailwind.config.js    # Estilo y diseño Tailwind
├── src/
│   ├── app/                  # FastAPI main application y enrutadores
│   ├── ai_agent/             # Consultor Audit IA (Claude 3.5 prompts y herramientas)
│   ├── database/             # Conexión local / Supabase
│   ├── ingestion/            # Pipelines de carga y autogeneración de datos
│   └── rules/                # Motor de las 14 reglas de negocio (fraud_rules.py)
├── tests/
│   └── test_rules.py         # Suite de pruebas automatizadas de reglas
└── docs/
    └── arquitectura.md       # Diagramas y decisiones de diseño técnico
```

---

## Ética, Privacidad y Limitaciones

*   **Sin Datos Reales (Cumplimiento GDPR/Ley de Datos):** Toda la información analizada y cargada por defecto en este prototipo es ficticia y simulada sintéticamente mediante algoritmos generativos. No contiene registros de pólizas ni nombres de clientes reales.
*   **Decisión Compartida (Human-in-the-loop):** El software actúa exclusivamente como un asistente de auditoría y priorizador de alertas. La confirmación, el descarte de casos y las acciones de cobro o rechazo de reclamos recaen enteramente en los analistas especializados autorizados por la aseguradora.
*   **Manejo de Falsos Positivos:** El motor está calibrado para favorecer la exhaustividad en alertas tempranas de fraude. Casos inusuales pero lícitos pueden marcarse temporalmente como sospechosos; por ello, la auditoría humana inicial es un requisito de diseño indiscutible.
