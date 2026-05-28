"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getSiniestros, getSiniestro, getEstadisticas, chatAgente, getNivelColor, type Siniestro, type Estadisticas, type SiniestroDetalle } from "@/lib/api";
import { scoreColor, scoreLabel, scoreWidth, puntajeLabel, puntajeWidth } from "@/lib/score";

function BarraScore({
  score,
  nivel,
  puntaje,
  puntajeMax = 20,
  className = "w-16",
}: {
  score: number;
  nivel?: string;
  puntaje?: number | null;
  puntajeMax?: number;
  className?: string;
}) {
  const color = scoreColor(score, nivel);
  const ancho = puntaje != null ? puntajeWidth(puntaje, puntajeMax) : scoreWidth(score);
  const etiqueta =
    puntaje != null ? puntajeLabel(puntaje, puntajeMax) : scoreLabel(score);

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <div className="flex-1 min-w-[4rem] bg-gray-200 rounded-full h-1.5">
        <div className={`h-1.5 rounded-full ${color}`} style={{ width: ancho }} />
      </div>
      <span className="font-semibold text-xs whitespace-nowrap">{etiqueta}</span>
    </div>
  );
}

function NivelBadge({ nivel }: { nivel: string }) {
  const c = getNivelColor(nivel);
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${c.bg} ${c.text}`}>
      {c.badge} {nivel}
    </span>
  );
}

function StatCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className={`text-2xl font-semibold mt-1 ${color ?? "text-gray-900"}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  );
}

function TablaSiniestros({ siniestros, onSelect }: { siniestros: Siniestro[]; onSelect: (s: Siniestro) => void }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 bg-gray-50 text-left text-xs text-gray-500 uppercase tracking-wide">
            <th className="px-4 py-3">ID Póliza</th>
            <th className="px-4 py-3">Ramo</th>
            <th className="px-4 py-3">Ciudad</th>
            <th className="px-4 py-3">Monto</th>
            <th className="px-4 py-3">Asegurado</th>
            <th className="px-4 py-3">Score</th>
            <th className="px-4 py-3">Nivel</th>
            <th className="px-4 py-3">Alertas</th>
          </tr>
        </thead>
        <tbody>
          {siniestros.map((s) => (
            <tr
              key={s.id_siniestro}
              onClick={() => onSelect(s)}
              className="border-b border-gray-50 hover:bg-blue-50 cursor-pointer transition-colors"
            >
              <td className="px-4 py-3 font-mono text-xs text-blue-700">{s.id_siniestro}</td>
              <td className="px-4 py-3">{s.ramo}</td>
              <td className="px-4 py-3 text-gray-600">{s.sucursal}</td>
              <td className="px-4 py-3 font-medium">${s.monto_reclamado?.toLocaleString()}</td>
              <td className="px-4 py-3 text-gray-600 max-w-[120px] truncate">{s.beneficiario}</td>
              <td className="px-4 py-3">
                <BarraScore
                  score={s.score}
                  nivel={s.nivel_riesgo}
                  puntaje={s.puntaje_total}
                  puntajeMax={s.puntaje_max ?? 20}
                />
              </td>
              <td className="px-4 py-3"><NivelBadge nivel={s.nivel_riesgo} /></td>
              <td className="px-4 py-3 text-center">
                <span className="inline-block bg-gray-100 text-gray-700 text-xs font-medium rounded-full px-2 py-0.5">
                  {s.num_alertas}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DetalleSiniestro({ siniestro, onClose }: { siniestro: Siniestro; onClose: () => void }) {
  const [detalle, setDetalle] = useState<SiniestroDetalle | null>(null);

  useEffect(() => {
    getSiniestro(siniestro.id_siniestro).then(setDetalle).catch(() => setDetalle(null));
  }, [siniestro.id_siniestro]);

  const d = detalle ?? siniestro;

  const nivelAlerta = (nivel: string) => {
    if (nivel === "ROJO") return { bg: "bg-red-50 border-red-200", dot: "bg-red-500", text: "text-red-800", icon: "🔴" };
    if (nivel === "AMARILLO") return { bg: "bg-yellow-50 border-yellow-200", dot: "bg-yellow-500", text: "text-yellow-800", icon: "🟡" };
    return { bg: "bg-green-50 border-green-200", dot: "bg-green-500", text: "text-green-800", icon: "🟢" };
  };

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-black/20" onClick={onClose}>
      <div
        className="w-full max-w-md bg-white shadow-2xl h-full overflow-y-auto p-6 space-y-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs text-gray-400 font-mono">{d.id_siniestro}</p>
            <h2 className="text-lg font-semibold">{d.ramo}</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-700 text-xl font-bold">×</button>
        </div>

        <div className="text-center py-4 bg-gray-50 rounded-xl">
          {d.puntaje_total != null ? (
            <>
              <p className="text-5xl font-bold text-gray-900">
                {Math.round(d.puntaje_total)}
                <span className="text-2xl text-gray-400 font-normal">/{d.puntaje_max ?? 20}</span>
              </p>
              <p className="text-sm text-gray-500 mt-1">Puntaje total (tabla SCORE_RIESGO)</p>
            </>
          ) : (
            <>
              <p className="text-5xl font-bold text-gray-900">
                {d.score}<span className="text-2xl text-gray-400 font-normal">/100</span>
              </p>
              <p className="text-sm text-gray-500 mt-1">Score de riesgo</p>
            </>
          )}
          <div className="mt-3 px-6">
            <BarraScore
              score={d.score}
              nivel={d.nivel_riesgo}
              puntaje={d.puntaje_total}
              puntajeMax={d.puntaje_max ?? 20}
              className="w-full"
            />
          </div>
          <p className="text-xs text-gray-500 mt-2">Score normalizado: {d.score}/100</p>
          <div className="mt-2"><NivelBadge nivel={d.nivel_riesgo} /></div>
          {d.accion_sugerida && (
            <p className="text-xs text-gray-600 mt-2 px-3">{d.accion_sugerida}</p>
          )}
        </div>

        <div className="space-y-1 text-sm">
          <div className="flex justify-between py-1 border-b border-gray-50">
            <span className="text-gray-500">Monto asegurado</span>
            <span className="font-medium">${d.monto_reclamado?.toLocaleString()}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-gray-50">
            <span className="text-gray-500">Asegurado</span>
            <span className="font-medium text-right max-w-[60%]">{d.asegurado_nombre || d.beneficiario}</span>
          </div>
          {d.asegurado_segmento && (
            <div className="flex justify-between py-1 border-b border-gray-50">
              <span className="text-gray-500">Segmento</span>
              <span className="font-medium">{d.asegurado_segmento}</span>
            </div>
          )}
          {d.asegurado_email && (
            <div className="flex justify-between py-1 border-b border-gray-50">
              <span className="text-gray-500">Email</span>
              <span className="text-xs">{d.asegurado_email}</span>
            </div>
          )}
          <div className="flex justify-between py-1 border-b border-gray-50">
            <span className="text-gray-500">Ciudad</span>
            <span>{d.sucursal}</span>
          </div>
          <div className="flex justify-between py-1 border-b border-gray-50">
            <span className="text-gray-500">Estado</span>
            <span>{d.estado}</span>
          </div>
          {d.poliza_prima && (
            <div className="flex justify-between py-1 border-b border-gray-50">
              <span className="text-gray-500">Prima</span>
              <span>${d.poliza_prima.toFixed(2)}</span>
            </div>
          )}
          {d.poliza_deducible && (
            <div className="flex justify-between py-1 border-b border-gray-50">
              <span className="text-gray-500">Deducible</span>
              <span>${d.poliza_deducible.toFixed(2)}</span>
            </div>
          )}
          {d.poliza_canal_venta && (
            <div className="flex justify-between py-1 border-b border-gray-50">
              <span className="text-gray-500">Canal venta</span>
              <span>{d.poliza_canal_venta}</span>
            </div>
          )}
        </div>

        {/* Señales desde POLIZA_PUNTAJE */}
        {detalle?.senales && detalle.senales.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-700 mb-2">
              📊 Señales de riesgo ({detalle.senales.length})
            </p>
            <div className="space-y-1.5 max-h-40 overflow-y-auto">
              {detalle.senales.map((s, i) => (
                <div key={i} className="flex justify-between text-xs bg-gray-50 rounded-lg px-3 py-2 border border-gray-100">
                  <span className="text-gray-700 pr-2">{s.senial}</span>
                  <span className="font-semibold text-gray-900 shrink-0">+{s.puntaje} pts</span>
                </div>
              ))}
            </div>
            {d.puntaje_senales != null && (
              <p className="text-xs text-right text-gray-500 mt-2 font-medium">
                Total señales: {d.puntaje_senales} pts
              </p>
            )}
          </div>
        )}

        {/* Alertas detectadas */}
        {detalle?.alertas && detalle.alertas.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1">
              ⚠️ Alertas detectadas ({detalle.alertas.length})
            </p>
            <div className="space-y-2">
              {detalle.alertas.map((a, i) => {
                const estilos = nivelAlerta(a.nivel);
                return (
                  <div key={i} className={`rounded-lg border p-3 ${estilos.bg}`}>
                    <div className="flex items-start gap-2">
                      <span className="text-base mt-0.5">{estilos.icon}</span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className={`text-xs font-semibold uppercase ${estilos.text}`}>{a.codigo}</span>
                          <span className={`ml-auto text-xs font-medium ${estilos.text}`}>+{a.puntos} pts</span>
                        </div>
                        <p className="text-xs text-gray-700 mt-0.5 leading-relaxed">{a.descripcion}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Resumen IA */}
        {d.resumen_ia && (
          <div className={`rounded-xl border p-4 ${
            d.nivel_riesgo === "ROJO" ? "bg-red-50 border-red-200" :
            d.nivel_riesgo === "AMARILLO" ? "bg-yellow-50 border-yellow-200" :
            "bg-green-50 border-green-200"
          }`}>
            <div className="flex items-start gap-2">
              <span className="text-base mt-0.5">
                {d.nivel_riesgo === "ROJO" ? "🔴" : d.nivel_riesgo === "AMARILLO" ? "🟡" : "🟢"}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-gray-700 mb-1">Resumen de alerta (IA)</p>
                <p className={`text-xs leading-relaxed ${
                  d.nivel_riesgo === "ROJO" ? "text-red-800" :
                  d.nivel_riesgo === "AMARILLO" ? "text-yellow-800" :
                  "text-green-800"
                }`}>
                  {d.resumen_ia}
                </p>
                <div className="mt-2">
                  <BarraScore
                    score={d.score}
                    nivel={d.nivel_riesgo}
                    puntaje={d.puntaje_total}
                    puntajeMax={d.puntaje_max ?? 20}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        <p className="text-xs text-gray-400 italic text-center border-t border-gray-100 pt-3">
          Este análisis es una alerta para revisión humana, no una acusación de fraude.
        </p>
      </div>
    </div>
  );
}

function ChatAgente() {
  const [messages, setMessages] = useState<{ role: "user" | "ai"; text: string }[]>([
    { role: "ai", text: "Hola, soy tu analista de fraude. Puedes preguntarme: ¿cuáles son las 10 pólizas de mayor riesgo? ¿Qué ramos concentran más alertas? ¿Qué ciudades tienen más casos críticos?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const pregunta = input.trim();
    setMessages((m) => [...m, { role: "user", text: pregunta }]);
    setInput("");
    setLoading(true);
    try {
      const respuesta = await chatAgente(pregunta);
      setMessages((m) => [...m, { role: "ai", text: respuesta }]);
    } catch {
      setMessages((m) => [...m, { role: "ai", text: "Error al conectar con el agente. Verifica que la API esté activa." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 flex flex-col h-96">
      <div className="px-4 py-3 border-b border-gray-100">
        <p className="text-sm font-semibold text-gray-800">🤖 Agente de análisis</p>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 text-sm">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-xl px-3 py-2 text-sm leading-relaxed ${
              m.role === "user"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-800 prose prose-sm prose-gray max-w-none"
            }`}>
              {m.role === "user" ? (
                m.text
              ) : (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    table({ children }) {
                      return (
                        <div className="overflow-x-auto my-2">
                          <table className="min-w-full text-xs border-collapse border border-gray-300">
                            {children}
                          </table>
                        </div>
                      );
                    },
                    th({ children }) {
                      return (
                        <th className="border border-gray-300 bg-gray-200 px-2 py-1 text-left font-semibold">
                          {children}
                        </th>
                      );
                    },
                    td({ children }) {
                      return (
                        <td className="border border-gray-300 px-2 py-1">
                          {children}
                        </td>
                      );
                    },
                    strong({ children }) {
                      return <strong className="font-semibold text-gray-900">{children}</strong>;
                    },
                  }}
                >
                  {m.text}
                </ReactMarkdown>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-500 rounded-xl px-3 py-2 text-xs animate-pulse">
              Analizando...
            </div>
          </div>
        )}
      </div>
      <div className="p-3 border-t border-gray-100 flex gap-2">
        <input
          className="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="¿Cuáles son los casos más críticos?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button
          onClick={send}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white text-sm px-4 py-2 rounded-lg transition-colors"
        >
          Enviar
        </button>
      </div>
    </div>
  );
}

const PAGE_SIZE = 15;

export default function Dashboard() {
  const [siniestros, setSiniestros] = useState<Siniestro[]>([]);
  const [stats, setStats]           = useState<Estadisticas | null>(null);
  const [filtroNivel, setFiltroNivel] = useState("");
  const [selected, setSelected]     = useState<Siniestro | null>(null);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState("");
  const [offset, setOffset]         = useState(0);
  const [total, setTotal]           = useState(0);

  const paginaActual = Math.floor(offset / PAGE_SIZE) + 1;
  const totalPaginas = Math.ceil(total / PAGE_SIZE);

  useEffect(() => {
    setOffset(0);
  }, [filtroNivel]);

  useEffect(() => {
    const cargar = async () => {
      setLoading(true);
      try {
        const dataS = await getSiniestros({ nivel: filtroNivel || undefined, limit: PAGE_SIZE, offset });
        setSiniestros(dataS.siniestros);
        setTotal(dataS.total);
        try {
          setStats(await getEstadisticas());
        } catch {
          setStats(null);
        }
      } catch {
        setError("No se puede conectar con la API. Asegúrate de que el backend esté corriendo en :8000");
      } finally {
        setLoading(false);
      }
    };
    cargar();
  }, [filtroNivel, offset]);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-gray-900">🔍 Fraudia Claims</h1>
          <p className="text-xs text-gray-400">Analizador de pólizas de alto riesgo — hackIAthon 2026</p>
        </div>
        <a
          href="/api/exportar/csv"
          className="text-xs bg-gray-900 text-white px-3 py-1.5 rounded-lg hover:bg-gray-700 transition-colors"
        >
          ↓ Exportar CSV
        </a>
      </header>

      <main className="max-w-screen-xl mx-auto px-6 py-6 space-y-6">

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total pólizas"     value={stats.total_siniestros} />
            <StatCard label="Casos críticos 🔴"  value={stats.casos_criticos}   color="text-red-600" />
            <StatCard label="Score promedio"     value={stats.score_promedio}   sub="escala 0–100 (SCORE_RIESGO)" />
            <StatCard
              label="Casos medios 🟡"
              value={stats.distribucion_riesgo["AMARILLO"] ?? 0}
              color="text-yellow-600"
            />
          </div>
        )}

        <div className="flex gap-2 flex-wrap">
          {["", "ROJO", "AMARILLO", "VERDE"].map((n) => (
            <button
              key={n}
              onClick={() => setFiltroNivel(n)}
              className={`text-sm px-4 py-1.5 rounded-full border transition-colors ${
                filtroNivel === n
                  ? "bg-gray-900 text-white border-gray-900"
                  : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"
              }`}
            >
              {n === "" ? "Todos" : n === "ROJO" ? "🔴 Críticos" : n === "AMARILLO" ? "🟡 Medios" : "🟢 Bajos"}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            {loading ? (
              <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400 text-sm">
                Cargando pólizas...
              </div>
            ) : (
              <>
                <TablaSiniestros siniestros={siniestros} onSelect={setSelected} />
                <div className="flex items-center justify-between mt-2">
                  <p className="text-xs text-gray-400">
                    {total} póliza(s) — Pág. {paginaActual} de {totalPaginas || 1}
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))}
                      disabled={offset === 0}
                      className="text-xs px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      ← Anterior
                    </button>
                    <button
                      onClick={() => setOffset((o) => o + PAGE_SIZE)}
                      disabled={offset + PAGE_SIZE >= total}
                      className="text-xs px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-gray-600 hover:border-gray-400 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      Siguiente →
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
          <div>
            <ChatAgente />
          </div>
        </div>

      </main>

      {selected && <DetalleSiniestro siniestro={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
