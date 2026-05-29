"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Shield,
  Bell,
  HelpCircle,
  User,
  Users,
  FileText,
  AlertTriangle,
  Bot,
  ChevronDown,
  ChevronUp,
  LogOut,
  Target,
  Tag,
  Sparkles,
  RefreshCw,
  Download,
  ChevronLeft,
  ChevronRight,
  Search,
  CheckCircle,
  X
} from "lucide-react";
import {
  getSiniestros,
  getSiniestro,
  getEstadisticas,
  chatAgente,
  getNivelColor,
  type Siniestro,
  type Estadisticas,
  type SiniestroDetalle
} from "@/lib/api";
import {
  scoreColor,
  scoreLabel,
  scoreWidth,
  puntajeLabel,
  puntajeWidth
} from "@/lib/score";

function BarraScore({
  score,
  nivel,
  puntaje,
  puntajeMax = 100,
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

function StatCard({
  label,
  value,
  sub,
  color,
  icon: Icon
}: {
  label: string;
  value: string | number;
  sub?: string;
  color?: string;
  icon?: any;
}) {
  return (
    <div className="bg-white rounded-2xl border border-gray-200/80 p-5 shadow-sm hover:shadow-md transition-all duration-300 flex items-center justify-between">
      <div>
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">{label}</p>
        <p className={`text-3xl font-bold mt-1.5 ${color ?? "text-gray-900"}`}>{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
      </div>
      {Icon && (
        <div className="bg-gray-50 p-3 rounded-xl">
          <Icon className="text-gray-400" size={24} />
        </div>
      )}
    </div>
  );
}

function TablaSiniestros({
  siniestros,
  onSelect
}: {
  siniestros: Siniestro[];
  onSelect: (s: Siniestro) => void;
}) {
  return (
    <div className="overflow-x-auto rounded-2xl border border-gray-200 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50/50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
            <th className="px-6 py-4">ID Siniestro</th>
            <th className="px-6 py-4">Ramo</th>
            <th className="px-6 py-4">Ciudad</th>
            <th className="px-6 py-4">Monto Reclamado</th>
            <th className="px-6 py-4">Asegurado</th>
            <th className="px-6 py-4">Score de Riesgo</th>
            <th className="px-6 py-4">Nivel</th>
            <th className="px-6 py-4 text-center">Alertas</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {siniestros.length === 0 ? (
            <tr>
              <td colSpan={8} className="px-6 py-12 text-center text-gray-400 text-sm">
                No se encontraron siniestros con el filtro seleccionado.
              </td>
            </tr>
          ) : (
            siniestros.map((s) => (
              <tr
                key={s.id_siniestro}
                onClick={() => onSelect(s)}
                className="hover:bg-[#f8fafd] cursor-pointer transition-all duration-150"
              >
                <td className="px-6 py-4 font-mono text-xs text-[#3b59ca] font-semibold">{s.id_siniestro}</td>
                <td className="px-6 py-4 font-medium text-gray-900">{s.ramo}</td>
                <td className="px-6 py-4 text-gray-600">{s.sucursal}</td>
                <td className="px-6 py-4 font-semibold text-gray-900">${s.monto_reclamado?.toLocaleString()}</td>
                <td className="px-6 py-4 text-gray-600 max-w-[150px] truncate">{s.asegurado_nombre || s.beneficiario}</td>
                <td className="px-6 py-4">
                  <BarraScore
                    score={s.score}
                    nivel={s.nivel_riesgo}
                    puntaje={s.puntaje_total}
                    puntajeMax={s.puntaje_max ?? 20}
                    className="w-24"
                  />
                </td>
                <td className="px-6 py-4"><NivelBadge nivel={s.nivel_riesgo} /></td>
                <td className="px-6 py-4 text-center">
                  <span className="inline-flex items-center justify-center bg-gray-100 text-gray-700 text-xs font-bold rounded-full h-6 w-6">
                    {s.num_alertas}
                  </span>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

function DetalleSiniestro({
  siniestro,
  onClose
}: {
  siniestro: Siniestro;
  onClose: () => void;
}) {
  const [detalle, setDetalle] = useState<SiniestroDetalle | null>(null);

  useEffect(() => {
    getSiniestro(siniestro.id_siniestro).then(setDetalle).catch(() => setDetalle(null));
  }, [siniestro.id_siniestro]);

  const d = detalle ?? siniestro;

  const nivelAlerta = (nivel: string) => {
    if (nivel === "ROJO") return { bg: "bg-red-50/50 border-red-100", dot: "bg-red-500", text: "text-red-800", icon: "🔴" };
    if (nivel === "AMARILLO") return { bg: "bg-yellow-50/50 border-yellow-100", dot: "bg-yellow-500", text: "text-yellow-800", icon: "🟡" };
    return { bg: "bg-green-50/50 border-green-100", dot: "bg-green-500", text: "text-green-800", icon: "🟢" };
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs transition-opacity duration-300" onClick={onClose}>
      <div
        className="w-full max-w-lg bg-white shadow-2xl h-full overflow-y-auto p-8 space-y-6 flex flex-col transform transition-transform duration-300 animate-slide-left"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between border-b border-gray-100 pb-4">
          <div>
            <p className="text-xs text-gray-400 font-mono font-semibold tracking-wider uppercase">{d.id_siniestro}</p>
            <h2 className="text-xl font-bold text-gray-900 mt-1">{d.ramo}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-700 bg-gray-50 hover:bg-gray-100 p-1.5 rounded-lg transition-colors font-bold"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto pr-1 space-y-6">
          <div className="text-center py-6 bg-gray-50 rounded-2xl border border-gray-100">
            {d.puntaje_total != null ? (
              <>
                <p className="text-5xl font-extrabold text-gray-950">
                  {Math.round(d.puntaje_total)}
                  <span className="text-2xl text-gray-400 font-normal">/{d.puntaje_max ?? 20}</span>
                </p>
                <p className="text-xs font-medium text-gray-500 mt-1.5 uppercase tracking-wider">Puntaje total asignado</p>
              </>
            ) : (
              <>
                <p className="text-5xl font-extrabold text-gray-950">
                  {d.score}<span className="text-2xl text-gray-400 font-normal">/100</span>
                </p>
                <p className="text-xs font-medium text-gray-500 mt-1.5 uppercase tracking-wider">Score de riesgo</p>
              </>
            )}
            <div className="mt-4 px-8">
              <BarraScore
                score={d.score}
                nivel={d.nivel_riesgo}
                puntaje={d.puntaje_total}
                puntajeMax={d.puntaje_max ?? 20}
                className="w-full"
              />
            </div>
            <p className="text-[11px] text-gray-400 mt-2">Score normalizado: {d.score}/100</p>
            <div className="mt-2.5"><NivelBadge nivel={d.nivel_riesgo} /></div>
            {d.accion_sugerida && (
              <p className="text-xs font-semibold text-[#3b59ca] mt-3 px-6 leading-relaxed">{d.accion_sugerida}</p>
            )}
          </div>

          <div className="bg-white rounded-2xl border border-gray-200/80 p-5 space-y-3.5">
            <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider border-b border-gray-100 pb-2">
              Información de la Reclamación
            </h3>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <span className="text-gray-400 font-medium">Monto Asegurado</span>
                <p className="font-semibold text-gray-900 mt-0.5 text-sm">${d.monto_reclamado?.toLocaleString()}</p>
              </div>
              <div>
                <span className="text-gray-400 font-medium">Asegurado / Beneficiario</span>
                <p className="font-semibold text-gray-900 mt-0.5 truncate">{d.asegurado_nombre || d.beneficiario}</p>
              </div>
              {d.asegurado_segmento && (
                <div>
                  <span className="text-gray-400 font-medium">Segmento Cliente</span>
                  <p className="font-semibold text-gray-900 mt-0.5">{d.asegurado_segmento}</p>
                </div>
              )}
              {d.asegurado_email && (
                <div className="col-span-2">
                  <span className="text-gray-400 font-medium">Email Asegurado</span>
                  <p className="font-semibold text-gray-900 mt-0.5 truncate font-mono text-[11px]">{d.asegurado_email}</p>
                </div>
              )}
              <div>
                <span className="text-gray-400 font-medium">Ciudad / Sucursal</span>
                <p className="font-semibold text-gray-900 mt-0.5">{d.sucursal}</p>
              </div>
              <div>
                <span className="text-gray-400 font-medium">Estado Póliza</span>
                <p className="font-semibold text-gray-900 mt-0.5">{d.estado}</p>
              </div>
              {d.poliza_prima && (
                <div>
                  <span className="text-gray-400 font-medium">Prima Comercial</span>
                  <p className="font-semibold text-gray-900 mt-0.5">${d.poliza_prima.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                </div>
              )}
              {d.poliza_deducible && (
                <div>
                  <span className="text-gray-400 font-medium">Deducible Aplicado</span>
                  <p className="font-semibold text-gray-900 mt-0.5">${d.poliza_deducible.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                </div>
              )}
              {d.poliza_canal_venta && (
                <div className="col-span-2">
                  <span className="text-gray-400 font-medium">Canal de Venta</span>
                  <p className="font-semibold text-gray-900 mt-0.5">{d.poliza_canal_venta}</p>
                </div>
              )}
            </div>
          </div>

          {/* Señales desde POLIZA_PUNTAJE */}
          {detalle?.senales && detalle.senales.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                📊 Desglose de Señales de Riesgo ({detalle.senales.length})
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {detalle.senales.map((s, i) => (
                  <div key={i} className="flex items-center justify-between text-xs bg-gray-50 hover:bg-gray-100 transition-colors rounded-xl px-4 py-3 border border-gray-200/60 shadow-sm">
                    <span className="text-gray-700 font-medium leading-relaxed pr-3">{s.senial}</span>
                    <span className="font-bold text-red-600 shrink-0 bg-red-50 px-2 py-1 rounded-lg">+{s.puntaje} pts</span>
                  </div>
                ))}
              </div>
              {d.puntaje_senales != null && (
                <p className="text-xs text-right text-gray-400 font-bold">
                  Suma total señales: <span className="text-gray-800 text-sm font-extrabold">{d.puntaje_senales} pts</span>
                </p>
              )}
            </div>
          )}

          {/* Alertas detectadas */}
          {detalle?.alertas && detalle.alertas.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-gray-900 uppercase tracking-wider">
                ⚠️ Alertas del Motor de Reglas ({detalle.alertas.length})
              </h3>
              <div className="space-y-2.5">
                {detalle.alertas.map((a, i) => {
                  const estilos = nivelAlerta(a.nivel);
                  return (
                    <div key={i} className={`rounded-xl border p-4 shadow-sm ${estilos.bg} border-gray-200/50`}>
                      <div className="flex items-start gap-3">
                        <span className="text-base mt-0.5 shrink-0">{estilos.icon}</span>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center justify-between gap-2">
                            <span className={`text-xs font-extrabold uppercase tracking-wide ${estilos.text}`}>{a.codigo}</span>
                            <span className={`text-xs font-bold bg-white px-2 py-0.5 rounded-lg border border-gray-100 shadow-sm ${estilos.text}`}>+{a.puntos} pts</span>
                          </div>
                          <p className="text-xs text-gray-700 mt-1.5 leading-relaxed font-medium">{a.descripcion}</p>
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
            <div className={`rounded-2xl border p-5 shadow-sm ${
              d.nivel_riesgo === "ROJO" ? "bg-red-50/50 border-red-200/60" :
              d.nivel_riesgo === "AMARILLO" ? "bg-yellow-50/50 border-yellow-200/60" :
              "bg-green-50/50 border-green-200/60"
            }`}>
              <div className="flex items-start gap-3">
                <span className="text-base mt-0.5 shrink-0">
                  {d.nivel_riesgo === "ROJO" ? "🔴" : d.nivel_riesgo === "AMARILLO" ? "🟡" : "🟢"}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-bold text-gray-900 uppercase tracking-wider mb-2">Explicación del Score (IA)</p>
                  <p className={`text-xs leading-relaxed font-medium ${
                    d.nivel_riesgo === "ROJO" ? "text-red-900" :
                    d.nivel_riesgo === "AMARILLO" ? "text-yellow-900" :
                    "text-green-900"
                  }`}>
                    {d.resumen_ia}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-gray-100 pt-4 text-center">
          <p className="text-[10px] text-gray-400 italic">
            Este software genera alertas de posible riesgo de fraude para auditoría. Las decisiones finales corresponden al analista de la compañía.
          </p>
        </div>
      </div>
    </div>
  );
}

function ChatAgente({ fullScreen = false }: { fullScreen?: boolean }) {
  const [messages, setMessages] = useState<{ role: "user" | "ai"; text: string }[]>([
    {
      role: "ai",
      text: "Hola, soy **Audit IA**, tu asesor de riesgos y fraudes de seguros. Puedo consultar el dataset y responder preguntas estratégicas.\n\nPrueba preguntándome:\n- *¿Cuáles son los 10 siniestros de mayor riesgo?*\n- *¿Qué sucursales o ciudades concentran la mayor cantidad de alertas?*\n- *¿Qué proveedores o talleres registran el puntaje más alto?*\n- *¿Qué documentos faltan en los casos de riesgo crítico?*"
    },
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
      setMessages((m) => [
        ...m,
        { role: "ai", text: "**Error de conexión:** No se pudo obtener respuesta. Verifica que el servidor de la API esté activo en producción o localmente." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`bg-white rounded-2xl border border-gray-200 shadow-sm flex flex-col ${fullScreen ? "h-[calc(100vh-200px)]" : "h-[450px]"}`}>
      <div className="px-5 py-4 border-b border-gray-100 bg-gray-50/50 rounded-t-2xl flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot size={20} className="text-[#3b59ca]" />
          <p className="text-sm font-bold text-gray-800">Audit IA — Consultor Analítico</p>
        </div>
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-50 text-green-700 border border-green-200/50">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" /> Activo
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-4 text-sm scrollbar-thin">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-3 leading-relaxed shadow-sm ${
              m.role === "user"
                ? "bg-[#3b59ca] text-white rounded-tr-none"
                : "bg-gray-50 text-gray-800 rounded-tl-none border border-gray-100 prose prose-sm prose-slate max-w-none"
            }`}>
              {m.role === "user" ? (
                <p className="text-sm font-medium">{m.text}</p>
              ) : (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    table({ children }) {
                      return (
                        <div className="overflow-x-auto my-3 rounded-xl border border-gray-200 bg-white">
                          <table className="min-w-full text-xs border-collapse divide-y divide-gray-100">
                            {children}
                          </table>
                        </div>
                      );
                    },
                    thead({ children }) {
                      return <thead className="bg-gray-50 text-gray-600 font-semibold">{children}</thead>;
                    },
                    th({ children }) {
                      return (
                        <th className="px-3 py-2 text-left font-bold text-gray-700 uppercase tracking-wider">
                          {children}
                        </th>
                      );
                    },
                    tr({ children }) {
                      return <tr className="divide-x divide-gray-100 border-b border-gray-100 hover:bg-gray-50/50">{children}</tr>;
                    },
                    td({ children }) {
                      return (
                        <td className="px-3 py-2 text-gray-600 font-medium">
                          {children}
                        </td>
                      );
                    },
                    strong({ children }) {
                      return <strong className="font-bold text-gray-900">{children}</strong>;
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
            <div className="bg-gray-50 border border-gray-100 text-gray-500 rounded-2xl rounded-tl-none px-4 py-3 text-xs flex items-center gap-2 shadow-sm">
              <Bot size={16} className="text-[#3b59ca] animate-spin" />
              <span className="font-semibold animate-pulse">Audit IA está analizando los siniestros...</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-100 flex gap-2 bg-gray-50/30 rounded-b-2xl">
        <input
          className="flex-1 text-sm border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#3b59ca]/50 bg-white shadow-inner"
          placeholder="Ej: ¿Cuáles son los 10 siniestros con mayor riesgo?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <button
          onClick={send}
          disabled={loading}
          className="bg-[#3b59ca] hover:bg-[#2e47a3] disabled:bg-gray-300 text-white font-bold text-sm px-5 py-2.5 rounded-xl transition-all shadow-sm flex items-center gap-1.5"
        >
          <Sparkles size={16} /> Enviar
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

  // Layout states from screenshot
  const [activeTab, setActiveTab] = useState("poliza"); // Start on "poliza" to show the mock "Próximamente" from image, but allow toggling
  const [configOpen, setConfigOpen] = useState(true);
  const [floatingChatOpen, setFloatingChatOpen] = useState(false);

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
        setError("Error de comunicación: Asegúrate de que el backend de la API esté activo.");
      } finally {
        setLoading(false);
      }
    };
    cargar();
  }, [filtroNivel, offset]);

  const menuItems = [
    { id: "asegurado", name: "Asegurado", icon: User },
    { id: "beneficiario", name: "Beneficiario", icon: Users },
    { id: "poliza", name: "Póliza", icon: FileText },
    { id: "siniestro", name: "Siniestro", icon: AlertTriangle, badge: total > 0 ? total : undefined },
    { id: "agent", name: "Agente Lucho", icon: Bot },
  ];

  return (
    <div className="min-h-screen bg-[#f4f6fa] flex flex-col font-sans antialiased text-[#1c2434]">

      {/* HEADER EXACT TO SCREENSHOT */}
      <header className="bg-white border-b border-gray-200/80 px-6 py-3.5 flex items-center justify-between sticky top-0 z-30 shadow-sm">
        <div className="flex items-center gap-3.5">
          <div className="bg-[#eff2fc] p-2.5 rounded-xl border border-gray-100 flex items-center justify-center">
            <Shield className="text-[#3b59ca]" size={22} />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-gray-950 tracking-tight">Gestor de Reclamos</h1>
            <p className="text-[11px] text-gray-400 font-semibold">Rol Administrador</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button className="bg-white border border-gray-200 text-gray-500 hover:text-gray-800 p-2 rounded-xl shadow-sm hover:bg-gray-50 transition-all">
            <Bell size={18} />
          </button>
          <button className="bg-white border border-gray-200 text-gray-500 hover:text-gray-800 p-2 rounded-xl shadow-sm hover:bg-gray-50 transition-all">
            <HelpCircle size={18} />
          </button>

          <div className="flex items-center gap-3 bg-white border border-gray-100 rounded-2xl px-4 py-1.5 shadow-sm">
            <div className="bg-[#3b59ca] text-white rounded-full w-9 h-9 flex items-center justify-center font-bold text-xs tracking-wider">
              CM
            </div>
            <div className="text-left">
              <p className="text-xs font-bold text-gray-900">Carlos Mendoza</p>
              <p className="text-[9px] text-[#3b59ca] font-extrabold tracking-wider">ANALISTA SENIOR</p>
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 max-w-full">

        {/* SIDEBAR EXACT TO SCREENSHOT */}
        <aside className="w-72 p-5 flex flex-col shrink-0 sticky top-[73px] h-[calc(100vh-73px)] overflow-y-auto">
          <div className="bg-white rounded-2xl border border-gray-200/80 p-4 shadow-sm flex-1 flex flex-col justify-between">
            <nav className="space-y-1.5">
              {menuItems.map((item) => {
                const Icon = item.icon;
                const isSelected = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold tracking-wide transition-all ${
                      isSelected
                        ? "bg-[#eff2fc] text-[#3b59ca]"
                        : "text-gray-500 hover:bg-gray-50 hover:text-gray-800"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon size={18} className={isSelected ? "text-[#3b59ca]" : "text-gray-400"} />
                      <span>{item.name}</span>
                    </div>
                    {item.badge && (
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                        isSelected ? "bg-[#3b59ca] text-white" : "bg-gray-100 text-gray-600"
                      }`}>
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}

              {/* COLLAPSIBLE CONFIGURACIÓN */}
              <div className="pt-2">
                <button
                  onClick={() => setConfigOpen(!configOpen)}
                  className="w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold tracking-wide text-gray-500 hover:bg-gray-50 hover:text-gray-800"
                >
                  <div className="flex items-center gap-3">
                    <Target size={18} className="text-gray-400" />
                    <span>Configuración</span>
                  </div>
                  {configOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>

                {configOpen && (
                  <div className="pl-6 mt-1 space-y-1">
                    <button
                      onClick={() => setActiveTab("puntaje")}
                      className={`w-full flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                        activeTab === "puntaje"
                          ? "bg-[#eff2fc] text-[#3b59ca]"
                          : "text-gray-500 hover:bg-gray-50 hover:text-gray-800"
                      }`}
                    >
                      <Target size={14} className={activeTab === "puntaje" ? "text-[#3b59ca]" : "text-gray-400"} />
                      <span>Puntaje</span>
                    </button>
                    <button
                      onClick={() => setActiveTab("clasificacion")}
                      className={`w-full flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                        activeTab === "clasificacion"
                          ? "bg-[#eff2fc] text-[#3b59ca]"
                          : "text-gray-500 hover:bg-gray-50 hover:text-gray-800"
                      }`}
                    >
                      <Tag size={14} className={activeTab === "clasificacion" ? "text-[#3b59ca]" : "text-gray-400"} />
                      <span>Clasificación</span>
                    </button>
                  </div>
                )}
              </div>
            </nav>

            <div className="border-t border-gray-100 pt-4 mt-6 space-y-1.5">
              <button
                onClick={() => setActiveTab("perfil")}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === "perfil"
                    ? "bg-[#eff2fc] text-[#3b59ca]"
                    : "text-gray-500 hover:bg-gray-50 hover:text-gray-800"
                }`}
              >
                <User size={18} className={activeTab === "perfil" ? "text-[#3b59ca]" : "text-gray-400"} />
                <span>Perfil</span>
              </button>
              <button
                onClick={async () => {
                  try {
                    await fetch("http://localhost:8000/db/recargar", { method: "POST" });
                    window.location.reload();
                  } catch {
                    window.location.reload();
                  }
                }}
                className="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold text-red-500 hover:bg-red-50/50 transition-all"
              >
                <LogOut size={18} className="text-red-400" />
                <span>Cerrar Sesión</span>
              </button>
            </div>
          </div>
        </aside>

        {/* MAIN PANEL BASED ON CHOSEN SIDEBAR TAB */}
        <main className="flex-1 p-5 overflow-x-hidden">

          {/* TAB: PÓLIZA (Próximamente as in screenshot) */}
          {activeTab === "poliza" && (
            <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm flex flex-col items-center justify-center h-80">
              <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Póliza</h2>
              <p className="text-gray-400 text-sm mt-3 font-semibold">Próximamente.</p>
            </div>
          )}

          {/* TAB: ASEGURADO */}
          {activeTab === "asegurado" && (
            <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm flex flex-col items-center justify-center h-80 animate-fade-in">
              <User className="text-[#3b59ca] mb-4" size={48} />
              <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Módulo de Asegurados</h2>
              <p className="text-gray-400 text-sm mt-2 max-w-md mx-auto leading-relaxed">
                Gestión avanzada del perfil del asegurado, histórico de primas, contratos vigentes y nivel de siniestralidad acumulado.
              </p>
              <p className="text-[#3b59ca] text-xs font-bold mt-4 uppercase tracking-wider bg-[#eff2fc] px-3 py-1 rounded-full">Próximamente</p>
            </div>
          )}

          {/* TAB: BENEFICIARIO */}
          {activeTab === "beneficiario" && (
            <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm flex flex-col items-center justify-center h-80 animate-fade-in">
              <Users className="text-[#3b59ca] mb-4" size={48} />
              <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Módulo de Beneficiarios / Talleres</h2>
              <p className="text-gray-400 text-sm mt-2 max-w-md mx-auto leading-relaxed">
                Seguimiento de talleres mecánicos asignados, clínicas autorizadas y auditoría de proveedores en lista restrictiva.
              </p>
              <p className="text-[#3b59ca] text-xs font-bold mt-4 uppercase tracking-wider bg-[#eff2fc] px-3 py-1 rounded-full">Próximamente</p>
            </div>
          )}

          {/* TAB: CLASIFICACIÓN */}
          {activeTab === "clasificacion" && (
            <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm flex flex-col items-center justify-center h-80 animate-fade-in">
              <Tag className="text-[#3b59ca] mb-4" size={48} />
              <h2 className="text-2xl font-extrabold text-gray-900 tracking-tight">Reglas de Clasificación</h2>
              <p className="text-gray-400 text-sm mt-2 max-w-md mx-auto leading-relaxed">
                Configuración analítica para la clasificación semáforo (Verde, Amarillo, Rojo) de siniestros según regulaciones y políticas de la compañía.
              </p>
              <p className="text-[#3b59ca] text-xs font-bold mt-4 uppercase tracking-wider bg-[#eff2fc] px-3 py-1 rounded-full">Próximamente</p>
            </div>
          )}

          {/* TAB: PERFIL */}
          {activeTab === "perfil" && (
            <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm max-w-xl mx-auto space-y-6 animate-fade-in">
              <div className="flex items-center gap-4 border-b border-gray-100 pb-5">
                <div className="bg-[#3b59ca] text-white rounded-full w-16 h-16 flex items-center justify-center font-bold text-2xl">
                  CM
                </div>
                <div>
                  <h2 className="text-lg font-extrabold text-gray-950">Carlos Mendoza</h2>
                  <p className="text-xs text-gray-400 font-semibold uppercase tracking-wider">ANALISTA SENIOR DE FRAUDE</p>
                </div>
              </div>
              <div className="space-y-3.5 text-xs">
                <div className="flex justify-between py-1 border-b border-gray-50">
                  <span className="text-gray-400 font-medium">Departamento</span>
                  <span className="font-semibold text-gray-900">Unidad Antifraude y Auditoría</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-50">
                  <span className="text-gray-400 font-medium">Ubicación / Sucursal</span>
                  <span className="font-semibold text-gray-900">Oficina Principal, Quito</span>
                </div>
                <div className="flex justify-between py-1 border-b border-gray-50">
                  <span className="text-gray-400 font-medium">Nivel de Acceso</span>
                  <span className="font-semibold text-[#3b59ca] bg-[#eff2fc] px-2.5 py-0.5 rounded-lg">Administrador</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB: CONFIGURACIÓN PUNTAJE */}
          {activeTab === "puntaje" && (
            <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm space-y-6 max-w-3xl mx-auto animate-fade-in">
              <div>
                <h2 className="text-xl font-extrabold text-gray-900 tracking-tight">Límites y Rangos del Score de Riesgo</h2>
                <p className="text-xs text-gray-400 mt-1 font-semibold">Configuración de niveles de riesgo del motor determinista</p>
              </div>

              <div className="space-y-4">
                <div className="flex items-start gap-4 p-4 rounded-xl border border-green-200 bg-green-50/50">
                  <span className="text-xl mt-0.5">🟢</span>
                  <div>
                    <h3 className="text-xs font-bold text-green-800 uppercase tracking-wider">Riesgo Bajo (0 - 40 pts)</h3>
                    <p className="text-xs text-green-700 mt-1 leading-relaxed">
                      Siniestros con pocas o ninguna alerta activada. Se aprueban automáticamente en el flujo express de la aseguradora.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-xl border border-yellow-200 bg-yellow-50/50">
                  <span className="text-xl mt-0.5">🟡</span>
                  <div>
                    <h3 className="text-xs font-bold text-yellow-800 uppercase tracking-wider">Riesgo Medio / Escalamiento (41 - 75 pts)</h3>
                    <p className="text-xs text-yellow-700 mt-1 leading-relaxed">
                      Siniestros con acumulación de alertas documentales o demoras leves. Requiere auditoría y revisión de expedientes físicos.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 rounded-xl border border-red-200 bg-red-50/50">
                  <span className="text-xl mt-0.5">🔴</span>
                  <div>
                    <h3 className="text-xs font-bold text-red-800 uppercase tracking-wider">Riesgo Crítico / Inspección (76 - 100 pts)</h3>
                    <p className="text-xs text-red-700 mt-1 leading-relaxed">
                      Siniestros de severidad máxima o con alertas críticas activas (lista restrictiva, posible falsificación). Suspende el pago e inicia investigación de campo inmediata.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB: AGENTE Audit (Full Screen Chat) */}
          {activeTab === "agent" && (
            <div className="space-y-4 max-w-4xl mx-auto animate-fade-in">
              <div>
                <h2 className="text-xl font-extrabold text-gray-900 tracking-tight">Audit IA — Chat Conversacional</h2>
                <p className="text-xs text-gray-400 mt-1 font-semibold">Realiza consultas analíticas avanzadas utilizando lenguaje natural</p>
              </div>
              <ChatAgente fullScreen={true} />
            </div>
          )}

          {/* TAB: SINIESTRO (The main Claims dashboard fully updated) */}
          {activeTab === "siniestro" && (
            <div className="space-y-6 animate-fade-in">

              {/* TOP ACTIONS */}
              <div className="flex items-center justify-between flex-wrap gap-4 border-b border-gray-200/50 pb-4">
                <div>
                  <h2 className="text-xl font-extrabold text-gray-900 tracking-tight">Análisis de Siniestros</h2>
                  <p className="text-xs text-gray-400 mt-1 font-semibold">Búsqueda y priorización de reclamaciones por riesgo de fraude</p>
                </div>
                <div className="flex items-center gap-2.5">
                  <button
                    onClick={async () => {
                      try {
                        await fetch("http://localhost:8000/db/recargar", { method: "POST" });
                        window.location.reload();
                      } catch {
                        window.location.reload();
                      }
                    }}
                    className="text-xs bg-[#3b59ca] text-white px-4 py-2.5 rounded-xl hover:bg-[#2e47a3] transition-all font-bold flex items-center gap-1.5 shadow-sm"
                  >
                    <RefreshCw size={14} /> Recargar Datos
                  </button>
                  <a
                    href="http://localhost:8000/exportar/csv"
                    className="text-xs bg-gray-900 text-white px-4 py-2.5 rounded-xl hover:bg-gray-800 transition-all font-bold flex items-center gap-1.5 shadow-sm"
                  >
                    <Download size={14} /> Exportar Casos (CSV)
                  </a>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded-2xl px-5 py-4 text-xs font-semibold shadow-sm">
                  {error}
                </div>
              )}

              {/* STATISTICS CARDS */}
              {stats && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                  <StatCard label="Total reclamaciones" value={stats.total_siniestros} icon={FileText} />
                  <StatCard label="Casos críticos 🔴" value={stats.casos_criticos} color="text-red-600" icon={AlertTriangle} />
                  <StatCard label="Score promedio" value={stats.score_promedio} sub="Escala 0–100" icon={Target} />
                  <StatCard
                    label="Casos medios 🟡"
                    value={stats.distribucion_riesgo["AMARILLO"] ?? 0}
                    color="text-yellow-600"
                    icon={AlertTriangle}
                  />
                </div>
              )}

              {/* SEMÁFORO FILTERS */}
              <div className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm flex items-center justify-between flex-wrap gap-4">
                <div className="flex gap-2 flex-wrap">
                  {["", "ROJO", "AMARILLO", "VERDE"].map((n) => (
                    <button
                      key={n}
                      onClick={() => setFiltroNivel(n)}
                      className={`text-xs font-bold px-4 py-2 rounded-xl border transition-all ${
                        filtroNivel === n
                          ? "bg-gray-900 text-white border-gray-900 shadow-sm"
                          : "bg-white text-gray-500 border-gray-200 hover:border-gray-400 hover:text-gray-800"
                      }`}
                    >
                      {n === "" ? "Todos los casos" : n === "ROJO" ? "🔴 Críticos" : n === "AMARILLO" ? "🟡 Medios" : "🟢 Bajos"}
                    </button>
                  ))}
                </div>
                <div className="text-xs text-gray-400 font-bold uppercase tracking-wider">
                  prioridad de cartera
                </div>
              </div>

              {/* TABLE CONTAINER */}
              <div>
                {loading ? (
                  <div className="bg-white rounded-2xl border border-gray-200 p-16 text-center text-gray-400 text-xs font-bold animate-pulse shadow-sm">
                    Sincronizando pólizas y cargando análisis...
                  </div>
                ) : (
                  <div className="space-y-3">
                    <TablaSiniestros siniestros={siniestros} onSelect={setSelected} />
                    <div className="flex items-center justify-between mt-2.5">
                      <p className="text-[11px] text-gray-400 font-bold">
                        {total} siniestro(s) encontrados — Página {paginaActual} de {totalPaginas || 1}
                      </p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setOffset((o) => Math.max(0, o - PAGE_SIZE))}
                          disabled={offset === 0}
                          className="text-xs font-bold px-4 py-2 rounded-xl border border-gray-200 bg-white text-gray-500 hover:border-gray-400 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
                        >
                          <ChevronLeft size={16} className="inline mr-1" /> Anterior
                        </button>
                        <button
                          onClick={() => setOffset((o) => o + PAGE_SIZE)}
                          disabled={offset + PAGE_SIZE >= total}
                          className="text-xs font-bold px-4 py-2 rounded-xl border border-gray-200 bg-white text-gray-500 hover:border-gray-400 hover:text-gray-800 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm"
                        >
                          Siguiente <ChevronRight size={16} className="inline ml-1" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* FLOATING ACTION BUTTON (FAB) EXACT TO SCREENSHOT */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setFloatingChatOpen(!floatingChatOpen)}
          className="bg-gradient-to-tr from-[#3b59ca] to-indigo-600 text-white rounded-full p-5 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 flex items-center justify-center border border-white/20 animate-bounce-slow"
        >
          {floatingChatOpen ? <X size={24} /> : <Sparkles size={24} />}
        </button>
      </div>

      {/* FLOATING IA CHAT POPUP */}
      {floatingChatOpen && (
        <div className="fixed bottom-24 right-6 w-96 z-40 animate-slide-up">
          <ChatAgente />
        </div>
      )}

      {selected && <DetalleSiniestro siniestro={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
