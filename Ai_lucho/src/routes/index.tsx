import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Superpoderosos — Auditor Agéntico de Facturación de Siniestros" },
      {
        name: "description",
        content:
          "Equipo Superpoderosos en Hackiathon 2026: agente IA que audita facturas de talleres vs tarifario y siniestralidad, detectando discrepancias y cobros duplicados.",
      },
      { property: "og:title", content: "Superpoderosos — Auditor Agéntico de Facturación" },
      {
        property: "og:description",
        content:
          "Agente que audita automáticamente documentación y facturas enviadas por talleres a aseguradoras.",
      },
    ],
  }),
  component: Index,
});

const steps = [
  {
    n: "01",
    title: "Análisis",
    desc: "Mapeamos el flujo actual desde el contrato de seguros, el reclamo y el analisis del riesgo",
    video: "https://foto01publico.blob.core.windows.net/video01cotizador/01_Analisis.mp4",
    openInNewTab: true,
  },
  {
    n: "02",
    title: "Ejecutivo Operativo",
    desc: "Diseñamos una aplicacion web centrada en el reclamo y asistido por AI - LUCHO",
    video: "https://foto01publico.blob.core.windows.net/video01cotizador/02_Ejecutivo_Operativo.mp4",
    openInNewTab: true,
  },
  {
    n: "03",
    title: "Ejecutivo Ajustador",
    desc: "El ejecutivo puede comunicarse con la AI Lucho desde el lugar del reclamo o el taller mediante voz o texto para establecer el puntaje de Riesgo.",
    video: "https://foto01publico.blob.core.windows.net/video01cotizador/03_Ejecutivo_Ajustador.mp4" as string | null,
    openInNewTab: true,
  },
  {
    n: "04",
    title: "Ejecutivo Antifraude",
    desc: "El panel del ejecutivo antifraude utiliza herramienta de analitica de datos para detectar el fraude",
    video: "https://foto01publico.blob.core.windows.net/video01cotizador/04_Ejecutivo%20Antifraude.mp4" as string | null,
    openInNewTab: true,
  },
  {
    n: "05",
    title: "Código Fuente",
    desc: "Repositorio de codigo fuente",
    video: null as string | null,
    links: [
      { label: "Link del repositorio GIT Agente Auditor", url: "https://github.com/anchundiatech/Audit.ai" },
      { label: "Link de aplicacion agentica en vercel", url: "https://audit-ai-liart.vercel.app/" },
    ] as { label: string; url: string }[] | undefined,
  },
];

function Index() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-border">
        <div
          className="absolute inset-0 -z-10 opacity-60"
          style={{
            background:
              "radial-gradient(60% 50% at 20% 10%, oklch(0.7 0.18 260 / 0.25), transparent 60%), radial-gradient(50% 40% at 90% 30%, oklch(0.75 0.15 30 / 0.25), transparent 60%)",
          }}
        />
        <div className="mx-auto max-w-6xl px-6 pt-24 pb-20 md:pt-32 md:pb-28">
          <a
            href="https://hackiathon.dev/"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-xs font-medium text-muted-foreground hover:text-foreground"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-primary" />
            Hackiathon 2026
          </a>
          <h1 className="mt-6 text-5xl font-bold tracking-tight md:text-7xl">
            Equipo <span className="italic">Superpoderosos</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-muted-foreground md:text-xl">
            Auditor Agéntico de Facturación de Siniestros — un agente que revisa automáticamente las reclamos y establece un PUNTAJE DE RIESGO para que el ejecutivo detecte el fraude a tiempo. 
          </p>

          <div className="mt-10 flex flex-wrap gap-3">
            <div className="rounded-2xl border border-border bg-card px-5 py-4">
              <p className="text-xs uppercase tracking-wider text-muted-foreground">Integrante</p>
              <p className="text-base font-semibold">Alejandro Achundia</p>
            </div>
            <div className="rounded-2xl border border-border bg-card px-5 py-4">
              <p className="text-xs uppercase tracking-wider text-muted-foreground">Integrante</p>
              <p className="text-base font-semibold">William Salazar</p>
            </div>
            <div className="rounded-2xl border border-border bg-card px-5 py-4">
              <p className="text-xs uppercase tracking-wider text-muted-foreground">Integrante</p>
              <p className="text-base font-semibold">Alicia Hurtado</p>
            </div>
          </div>
        </div>
      </section>

      {/* Problema */}
      <section className="border-b border-border">
        <div className="mx-auto grid max-w-6xl gap-10 px-6 py-20 md:grid-cols-3">
          <div>
            <p className="text-sm font-medium uppercase tracking-widest text-primary">
              El problema
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
              Siniestros sin auditar ocasion perdidas a la Cia de Seguros
            </h2>
          </div>
          <div className="md:col-span-2 text-lg leading-relaxed text-muted-foreground space-y-4">
            <p>
              En una aseguradora, los siniestros pueden presentar señales de riesgo que no siempre son evidentes en una revisión individual. Algunas alertas aparecen al cruzar variables de pólizas, asegurados, proveedores, documentos, fechas, montos e historial de reclamos.
            </p>
            <ul className="list-disc pl-5 space-y-1 text-base">
              <li>Frecuencia inusual de reclamos por asegurado o póliza.</li>
              <li>Montos reclamados superiores al promedio del ramo o del tipo de siniestro.</li>
              <li>Repetición de beneficiarios, proveedores, talleres, intermediarios asociados a casos observados.</li>
              <li>Reclamos ocurridos muy cerca de la fecha de inicio y fin de vigencia de la póliza.</li>
              <li>Documentos incompletos, ilegibles o inconsistentes.</li>
              <li>Narrativas similares entre diferentes reclamos.</li>
              <li>Cambios recientes en datos del asegurado antes del siniestro.</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Steps */}
      <section className="mx-auto max-w-6xl px-6 py-24">
        <div className="mb-16 max-w-2xl">
          <p className="text-sm font-medium uppercase tracking-widest text-primary">Proceso</p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight md:text-4xl">
            Cómo lo construimos
          </h2>
        </div>

        <ol className="relative space-y-20">
          <div className="absolute left-6 top-2 bottom-2 w-px bg-border md:left-8" aria-hidden />
          {steps.map((s) => (
            <li key={s.n} className="relative grid gap-8 pl-20 md:grid-cols-[1fr_1.2fr] md:gap-12 md:pl-24">
              <div className="absolute left-0 top-0 flex h-12 w-12 items-center justify-center rounded-full border border-border bg-card text-sm font-bold md:h-16 md:w-16 md:text-base">
                {s.n}
              </div>
              <div>
                <h3 className="text-2xl font-bold tracking-tight md:text-3xl">{s.title}</h3>
                <p className="mt-4 text-base leading-relaxed text-muted-foreground">{s.desc}</p>
              </div>
              <div className="overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
                {s.video ? (
                  s.openInNewTab ? (
                    <a
                      href={s.video}
                      target="_blank"
                      rel="noreferrer"
                      className="group relative block aspect-video h-full w-full"
                    >
                      <video
                        src={s.video}
                        muted
                        playsInline
                        preload="metadata"
                        className="aspect-video h-full w-full object-cover"
                      />
                      <div className="absolute inset-0 flex items-center justify-center bg-black/40 transition-colors group-hover:bg-black/60">
                        <span className="rounded-full bg-primary px-5 py-2 text-sm font-semibold text-primary-foreground shadow-lg">
                          ▶ Abrir video en nueva ventana
                        </span>
                      </div>
                    </a>
                  ) : (
                    <video
                      src={s.video}
                      controls
                      playsInline
                      preload="metadata"
                      className="aspect-video h-full w-full object-cover"
                    />
                  )
                ) : s.links && s.links.length > 0 ? (
                  <ol className="flex h-full flex-col justify-center gap-4 p-6 md:p-8">
                    {s.links.map((l, i) => {
                      const highlight = i === 1;
                      return (
                        <li
                          key={l.url}
                          className={
                            "flex items-start gap-3 rounded-xl p-3 " +
                            (highlight ? "border-2 border-red-500 bg-red-500/10 shadow-lg shadow-red-500/20" : "")
                          }
                        >
                          <span
                            className={
                              "flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-bold " +
                              (highlight
                                ? "bg-red-500 text-white"
                                : "border border-border")
                            }
                          >
                            {i + 1}
                          </span>
                          <div className="min-w-0">
                            <p className={"text-sm " + (highlight ? "font-semibold text-red-500" : "text-muted-foreground")}>
                              {l.label}
                            </p>
                            <a
                              href={l.url}
                              target="_blank"
                              rel="noreferrer"
                              className={
                                "break-all text-base font-semibold hover:underline " +
                                (highlight ? "text-red-500" : "text-primary")
                              }
                            >
                              {l.url} ↗
                            </a>
                          </div>
                        </li>
                      );
                    })}
                  </ol>
                ) : (
                  <div className="flex aspect-video items-center justify-center text-sm text-muted-foreground">
                    Video próximamente
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      </section>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-6 py-10 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
          <p>© 2026 Superpoderosos · Alejandro Achundia & William Salazar</p>
          <a
            href="https://hackiathon.dev/"
            target="_blank"
            rel="noreferrer"
            className="hover:text-foreground"
          >
            hackiathon.dev ↗
          </a>
        </div>
      </footer>
    </main>
  );
}
