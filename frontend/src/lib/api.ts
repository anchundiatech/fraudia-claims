const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Siniestro {
  id_siniestro: string;
  id_poliza: string;
  id_asegurado: string;
  ramo: string;
  cobertura: string;
  fecha_ocurrencia: string;
  monto_reclamado: number;
  estado: string;
  sucursal: string;
  beneficiario: string;
  score: number;
  nivel_riesgo: "VERDE" | "AMARILLO" | "ROJO";
  /** Puntaje validado 0–20 según SCORE_RIESGO */
  puntaje_total?: number;
  puntaje_max?: number;
  accion_sugerida?: string;
  num_alertas: number;
  resumen_ia: string;
  /** campos extra del detalle */
  poliza_prima?: number;
  poliza_deducible?: number;
  poliza_canal_venta?: string;
  poliza_ciudad?: string;
  asegurado_segmento?: string;
  asegurado_email?: string;
  asegurado_score?: number;
  /** Puntaje crudo en BD (analítica) */
  puntaje_bd?: number;
  /** Suma de puntajes en POLIZA_PUNTAJE */
  puntaje_senales?: number;
  senales?: { senial: string; puntaje: number; id_puntaje?: string }[];
  asegurado_nombre?: string;
  asegurado_apellido?: string;
  asegurado_tipo_documento?: string;
  asegurado_nro_documento?: string;
}

export interface Alerta {
  codigo: string;
  descripcion: string;
  puntos: number;
  nivel: string;
}

export interface Estadisticas {
  total_siniestros: number;
  distribucion_riesgo: Record<string, number>;
  score_promedio: number;
  top_ramos_riesgo: Record<string, number>;
  top_proveedores_alertas: Record<string, number>;
  top_sucursales_riesgo: Record<string, number>;
  casos_criticos: number;
}

export async function getSiniestros(params?: {
  nivel?: string;
  ramo?: string;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; siniestros: Siniestro[] }> {
  const qs = new URLSearchParams();
  if (params?.nivel)  qs.set("nivel", params.nivel);
  if (params?.ramo)   qs.set("ramo", params.ramo);
  if (params?.limit)  qs.set("limit", String(params.limit));
  if (params?.offset) qs.set("offset", String(params.offset));

  const res = await fetch(`${API_URL}/siniestros?${qs}`);
  if (!res.ok) throw new Error("Error al cargar siniestros");
  return res.json();
}

export async function getSiniestro(id: string): Promise<Siniestro & { alertas: Alerta[] }> {
  const res = await fetch(`${API_URL}/siniestros/${id}`);
  if (!res.ok) throw new Error("Siniestro no encontrado");
  return res.json();
}

export async function getEstadisticas(): Promise<Estadisticas> {
  const res = await fetch(`${API_URL}/estadisticas`);
  if (!res.ok) throw new Error("Error al cargar estadísticas");
  return res.json();
}

export interface SiniestroDetalle extends Siniestro {
  alertas: Alerta[];
  asegurado_segmento?: string;
  asegurado_email?: string;
  asegurado_score?: number;
  poliza_prima?: number;
  poliza_deducible?: number;
  poliza_canal_venta?: string;
  asegurado_nombre?: string;
  asegurado_apellido?: string;
  asegurado_tipo_documento?: string;
  asegurado_nro_documento?: string;
}

export async function chatAgente(pregunta: string): Promise<string> {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pregunta }),
  });
  if (!res.ok) throw new Error("Error en el agente");
  const data = await res.json();
  return data.respuesta;
}

export interface AgentConfig {
  status: string;
  provider: string;
  model: string;
  modelo?: string;
  proveedor?: string;
}

export async function getAgentStatus(): Promise<AgentConfig> {
  const res = await fetch(`${API_URL}/chat/status`);
  if (!res.ok) throw new Error("Error al obtener estado del agente");
  return res.json();
}

export async function updateAgentConfig(provider: string, model?: string): Promise<AgentConfig> {
  const res = await fetch(`${API_URL}/chat/config`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, model }),
  });
  if (!res.ok) throw new Error("Error al actualizar configuración");
  return res.json();
}

export function getNivelColor(nivel: string) {
  switch (nivel) {
    case "ROJO":     return { bg: "bg-red-100",    text: "text-red-800",    badge: "🔴" };
    case "AMARILLO": return { bg: "bg-yellow-100", text: "text-yellow-800", badge: "🟡" };
    default:         return { bg: "bg-green-100",  text: "text-green-800",  badge: "🟢" };
  }
}
