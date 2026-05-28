/** Score y semáforo alineados con SCORE_RIESGO (puntaje 0–20 → score 0–100). */

export function nivelColor(nivel: string): string {
  if (nivel === "ROJO") return "bg-red-500";
  if (nivel === "AMARILLO") return "bg-yellow-500";
  return "bg-green-500";
}

export function scoreColor(score: number, nivel?: string): string {
  if (nivel) return nivelColor(nivel);
  if (score >= 76) return "bg-red-500";
  if (score >= 41) return "bg-yellow-500";
  return "bg-green-500";
}

export function scoreLabel(score: number): string {
  return `${Math.round(score)}/100`;
}

export function puntajeLabel(puntaje: number, max = 20): string {
  return `${Math.round(puntaje)}/${max}`;
}

export function scoreWidth(score: number): string {
  return `${Math.min(100, Math.max(0, score))}%`;
}

export function puntajeWidth(puntaje: number, max = 20): string {
  return `${Math.min(100, Math.max(0, (puntaje / max) * 100))}%`;
}
