import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BrowserRouter,
  NavLink,
  Route,
  Routes,
  useLocation,
  Navigate,
} from "react-router-dom";
import {
  QueryClient,
  QueryClientProvider,
  useQuery,
} from "@tanstack/react-query";
import {
  Activity,
  ArrowUpRight,
  BookOpen,
  Boxes,
  ChartNoAxesCombined,
  ChevronDown,
  CircleHelp,
  Coins,
  FlaskConical,
  Globe,
  LayoutDashboard,
  Menu,
  PanelLeftClose,
  Settings2,
  ShieldCheck,
  Users,
  X,
} from "lucide-react";
import { api, download } from "./services/api";
import { Loading, Notice } from "./components/ui";
import {
  Dashboard,
  Strategies,
  Products,
  Cohorts,
  Finances,
  Benchmarks,
  Reports,
  Methodology,
} from "./pages/analytics";
import { Simulator } from "./pages/simulator";
import { Study } from "./pages/study";
import type { Result, Scenario, SimulationInput, Strategy } from "./types";
import "./styles.css";

type AppState = {
  input: SimulationInput;
  setInput: (v: SimulationInput) => void;
  result: Result;
  notify: (v: string) => void;
};
const Context = createContext<AppState | null>(null);
export function useApp() {
  const value = useContext(Context);
  if (!value) throw new Error("Contexto ausente");
  return value;
}
const navigation = [
  ["/", "Visão geral", LayoutDashboard],
  ["/estrategias", "Estratégias", Boxes],
  ["/simulador", "Simulador", Settings2],
  ["/produtos", "Produtos e preços", Coins],
  ["/jogadores", "Jogadores e coortes", Users],
  ["/financas", "Finanças", ChartNoAxesCombined],
  ["/benchmarking", "Benchmarking", Globe],
  ["/relatorios", "Relatórios", BookOpen],
] as const;
const titles: Record<string, [string, string]> = {
  "/": ["Visão geral", "Uma visão clara para a sua próxima decisão."],
  "/estrategias": [
    "Estratégias comerciais",
    "Compare contribuição, custos e resultado.",
  ],
  "/simulador": [
    "Simulador financeiro",
    "Transforme hipóteses em decisões fundamentadas.",
  ],
  "/produtos": [
    "Produtos e precificação",
    "Explore escolhas, preços e substituição.",
  ],
  "/jogadores": [
    "Jogadores e coortes",
    "Entenda a atividade ao longo de cada coorte.",
  ],
  "/financas": [
    "Finanças e viabilidade",
    "Acompanhe o resultado e a resistência do caixa.",
  ],
  "/benchmarking": [
    "Benchmarking de mercado",
    "Referências documentais, com contexto e limites.",
  ],
  "/relatorios": [
    "Relatórios e exportação",
    "Os mesmos números, prontos para sua análise.",
  ],
  "/metodologia": ["Metodologia e fontes", "Transparência em cada hipótese."],
  "/estudo": [
    "Arquivos do estudo",
    "Documentação e dados para uma análise reproduzível.",
  ],
};

function App() {
  const [input, setInput] = useState<SimulationInput>({
    strategy: "A",
    scenario: "central",
  });
  const [mobile, setMobile] = useState(false);
  const sidebarRef = useRef<HTMLElement>(null);
  const menuRef = useRef<HTMLButtonElement>(null);
  const [message, notify] = useState("");
  const location = useLocation();
  const title = titles[location.pathname] || titles["/"];
  const query = useQuery({
    queryKey: ["simulation", input],
    queryFn: () =>
      input.overrides
        ? api<Result>("/simulations/preview", "POST", input)
        : api<Result>(
            `/reference?strategy=${input.strategy}&scenario=${input.scenario}`,
          ),
    staleTime: 60000,
    retry: 1,
  });
  useEffect(() => {
    setMobile(false);
  }, [location.pathname]);
  useEffect(() => {
    if (!mobile) return;
    const focusable = () => Array.from(sidebarRef.current?.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), [tabindex="0"]') || []).filter(element=>element.getClientRects().length>0);
    focusable()[0]?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {event.preventDefault();setMobile(false);}
      if (event.key === "Tab") {
        const elements=focusable(), first=elements[0], last=elements[elements.length-1];
        if(event.shiftKey && document.activeElement===first){event.preventDefault();last?.focus();}
        else if(!event.shiftKey && document.activeElement===last){event.preventDefault();first?.focus();}
      }
    };
    document.addEventListener('keydown',onKey);
    return ()=>{document.removeEventListener('keydown',onKey);menuRef.current?.focus();};
  }, [mobile]);
  useEffect(() => {
    if (message) {
      const id = setTimeout(() => notify(""), 6000);
      return () => clearTimeout(id);
    }
  }, [message]);
  const exportPdf = async () => {
    try {
      await download(input, "pdf");
      notify("Relatório gerado com as hipóteses da execução selecionada.");
    } catch (e) {
      notify((e as Error).message);
    }
  };
  return (
    <>
      <a className="skip" href="#main">
        Ir para o conteúdo
      </a>
      <aside ref={sidebarRef} id="study-navigation" aria-label="Navegação do estudo" role={mobile ? "dialog" : undefined} aria-modal={mobile || undefined} className={`sidebar ${mobile ? "open" : ""}`}>
        <button className="mobile-menu sidebar-close" aria-label="Fechar menu" onClick={()=>setMobile(false)}><X size={18}/></button>
        <a className="brand" href="/">
          <span className="brand-symbol">
            <Activity size={22} />
          </span>
          datavoxen<span className="brand-dot">®</span>
        </a>
        <div className="workspace">
          <span className="workspace-icon">Ó</span>
          <div>
            <strong>Ilhas de Órion</strong>
            <span>Estúdio Horizonte</span>
          </div>
          <ChevronDown size={14} />
        </div>
        <span className="nav-label">ESTUDO PÚBLICO</span>
        <nav aria-label="Navegação principal">
          {navigation.map(([path, label, Icon]) => (
            <NavLink key={path} to={path} end={path === "/"}>
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="study-note">
            <FlaskConical size={18} />
            <strong>Uma hipótese. Muitas decisões.</strong>
            <p>Explore o estudo com transparência sobre dados e premissas.</p>
            <NavLink to="/metodologia">
              Conhecer a metodologia <ArrowUpRight size={14} />
            </NavLink>
          </div>
          <NavLink to="/metodologia" className="secondary-link">
            <CircleHelp size={17} />
            Metodologia e fontes
          </NavLink>
          <NavLink to="/estudo" className="user">
            <div className="avatar">DV</div>
            <span>
              <strong>Acervo do estudo</strong>
              <small>PDF, SQLite e dados públicos</small>
            </span>
            <ArrowUpRight size={16} />
          </NavLink>
        </div>
      </aside>
      {mobile && (
        <button
          className="sidebar-overlay"
          aria-label="Fechar navegação"
          onClick={() => setMobile(false)}
        />
      )}
      <div className="main-shell" inert={mobile}>
        <div className="topbar">
          <button
            ref={menuRef}
            className="mobile-menu"
            aria-label="Abrir navegação"
            aria-controls="study-navigation"
            aria-expanded={mobile}
            onClick={() => setMobile(true)}
          >
            <Menu size={21} />
          </button>
          <div className="breadcrumb">
            <PanelLeftClose size={16} />
            <span>Estudo</span>
            <span>/</span>
            <strong>{title[0]}</strong>
          </div>
          <div className="topbar-right">
            <span className="status-dot" />
            Modelo 2026.1
            <span className="divider" />
            <ShieldCheck size={15} />
            <span>Dados simulados</span>
          </div>
        </div>
        <main id="main">
          <header className="page-header">
            <div>
              <div className="eyebrow">INTELIGÊNCIA PARA DECIDIR</div>
              <h1>{title[0]}</h1>
              <p>{title[1]}</p>
            </div>
            <button className="button" onClick={exportPdf}>
              <BookOpen size={15} />
              Exportar relatório
              <ArrowUpRight size={14} />
            </button>
          </header>
          <div className="filter-bar">
            <div className="selection">
              <label>
                Estratégia
                <select
                  aria-label="Estratégia"
                  value={input.strategy}
                  onChange={(e) =>
                    setInput({
                      strategy: e.target.value as Strategy,
                      scenario: input.scenario,
                    })
                  }
                >
                  <option value="A">A · Venda direta</option>
                  <option value="B">B · Passe prioritário</option>
                  <option value="C">C · Modelo híbrido</option>
                </select>
              </label>
              <span className="filter-divider" />
              <label>
                Cenário
                <select
                  aria-label="Cenário"
                  value={input.scenario}
                  onChange={(e) =>
                    setInput({
                      strategy: input.strategy,
                      scenario: e.target.value as Scenario,
                    })
                  }
                >
                  <option value="central">Central</option>
                  <option value="conservador">Conservador</option>
                  <option value="otimista">Otimista</option>
                  <option value="estresse">Estresse</option>
                </select>
              </label>
            </div>
            <div className="period">
              <span className="pill">
                {input.overrides ? "Personalizado" : "Referência oficial"}
              </span>
              <span>Horizonte de 12 meses</span>
            </div>
          </div>
          {message && (
            <div className="toast" role="status">
              {message}
              <button aria-label="Fechar mensagem" onClick={() => notify("")}>
                <X size={15} />
              </button>
            </div>
          )}
          {query.isPending ? (
            <Loading />
          ) : query.isError ? (
            <Notice error>
              {query.error.message}{" "}
              <button onClick={() => query.refetch()}>Tentar novamente</button>
            </Notice>
          ) : (
            <Context.Provider
              value={{
                input,
                setInput,
                result: query.data,
                notify,
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/estrategias" element={<Strategies />} />
                <Route path="/simulador" element={<Simulator />} />
                <Route path="/produtos" element={<Products />} />
                <Route path="/jogadores" element={<Cohorts />} />
                <Route path="/financas" element={<Finances />} />
                <Route path="/benchmarking" element={<Benchmarks />} />
                <Route path="/relatorios" element={<Reports />} />
                <Route path="/metodologia" element={<Methodology />} />
                <Route path="/estudo" element={<Study />} />
                <Route
                  path="/conta"
                  element={<Navigate to="/estudo" replace />}
                />
                <Route
                  path="*"
                  element={
                    <Notice>
                      Página não encontrada. Use a navegação lateral.
                    </Notice>
                  }
                />
              </Routes>
            </Context.Provider>
          )}
          <footer>
            <span>Datavoxen · Estudo estratégico independente</span>
            <span>
              Ilhas de Órion é um jogo fictício. Resultados condicionais às
              hipóteses.
            </span>
          </footer>
        </main>
      </div>
    </>
  );
}
const client = new QueryClient({
  defaultOptions: { queries: { retry: 1, refetchOnWindowFocus: false } },
});
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={client}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
);
