# Arquitectura del sistema — Fraudia Claims

## Diagrama general

```
┌─────────────────────────────────────────────────────┐
│                   Usuario (Analista)                 │
└─────────────────────┬───────────────────────────────┘
                      │ Browser
┌─────────────────────▼───────────────────────────────┐
│            Frontend — Next.js 14 (Puerto 3000)       │
│  Dashboard · Tabla siniestros · Chat agente · KPIs   │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP REST
┌─────────────────────▼───────────────────────────────┐
│            Backend — Python FastAPI (Puerto 8000)    │
│                                                      │
│  /siniestros      → Lista con score calculado        │
│  /siniestros/:id  → Detalle + alertas                │
│  /estadisticas    → KPIs del dashboard               │
│  /chat            → Agente Claude (lenguaje natural) │
│  /exportar/csv    → Exportación de casos             │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Motor Reglas │  │ NLP Similitud│  │ Claude API │ │
│  │ (12 señales) │  │ (TF-IDF)     │  │ (Agente)   │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│         Dataset (CSV sintético / SQLite)             │
│  siniestros · pólizas · asegurados · proveedores     │
└─────────────────────────────────────────────────────┘
```

## Decisiones técnicas

- **Next.js + FastAPI separados**: permite escalar frontend y backend independientemente.
- **Motor de reglas en Python puro**: trazable, auditable y sin dependencia de ML para el score base.
- **Claude como agente explicativo**: responde preguntas en lenguaje natural con contexto real del dataset.
- **CSV como fuente de datos**: facilita la demo sin necesidad de configurar una BD.
- **Sin datos personales reales**: todo el dataset es sintético, generado con Faker/Python.
