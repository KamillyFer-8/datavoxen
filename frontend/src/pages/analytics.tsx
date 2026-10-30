import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowRight,
  ArrowUpRight,
  CircleDashed,
  ExternalLink,
  TrendingDown,
  Wallet,
  BadgeDollarSign,
  ReceiptText,
  ChartNoAxesCombined,
  Hourglass,
  Users,
  UserRoundCheck,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useApp } from "../main";
import { api, download } from "../services/api";
import {
  Bars,
  brl,
  Card,
  DataTable,
  Loading,
  Metric,
  MoneyChart,
  Notice,
  number,
  percent,
  Waterfall,
} from "../components/ui";
import type { Benchmark, Cohort, Month, Result, Summary } from "../types";

const names = {
  A: "Venda direta",
  B: "Passe prioritário",
  C: "Modelo híbrido",
};
function ExtendedMetrics({ result: r }: { result: Result }) {
  return (
    <div className="metrics">
      <Metric
        label="LTV parcial · coorte M1"
        icon={Hourglass}
        value={brl(r.summary.ltv_partial)}
        note="Contribuição por adquirido · 12 meses"
        help="Coorte M1, antes de CAC e custos fixos. Não é valor vitalício observado."
      />
      <Metric
        label="ARPU bruto mensal"
        icon={Users}
        value={brl(r.summary.arpu)}
        note="Por jogador-mês ativo"
        help="Receita bruta ÷ soma de ativos mensais. Não usa jogadores únicos anuais."
      />
      <Metric
        label="ARPPU bruto mensal"
        icon={UserRoundCheck}
        value={brl(r.summary.arppu)}
        note="Por comprador-mês"
        help="Receita bruta ÷ soma de compradores mensais. Pessoas podem aparecer em vários meses."
      />
      <Metric
        label="Jogadores adquiridos"
        icon={Users}
        value={number(r.summary.acquired)}
        note="Coortes distintas · M1 a M12"
        help="Volume de novas contas adquirido em cada mês, somado no horizonte."
      />
    </div>
  );
}
export function Dashboard() {
  const { result: r } = useApp();
  const s = r.summary;
  return (
    <>
      <div className="section-caption">
        <h2>O desempenho em perspectiva</h2>
        <span className="muted">Projeção acumulada · M1 a M12</span>
      </div>
      <div className="metrics">
        <Metric
          label="Receita bruta"
          icon={Wallet}
          value={brl(s.gross)}
          note="Antes de reembolsos, tarifas e tributos"
          help="Soma das unidades esperadas × preço × multiplicador de gasto. Valores esperados, sem vendas reais."
        />
        <Metric
          label="Receita após deduções"
          icon={BadgeDollarSign}
          value={brl(s.net)}
          note="Receita disponível antes dos custos"
          help="Reembolso sobre o bruto; plataforma e tributos incidem na base após reembolso."
        />
        <Metric
          label="Custos totais"
          icon={ReceiptText}
          value={brl(s.costs)}
          note="Operação, aquisição, produção e entrega"
          help="Inclui custos variáveis, produção inicial, três atualizações de conteúdo, operação e mídia."
        />
        <Metric
          label="Resultado financeiro"
          icon={ChartNoAxesCombined}
          value={brl(s.flow)}
          note="Receita após deduções menos custos"
          help="Resultado de 12 meses. Caixa considera capital inicial; resultado não inclui o capital como receita."
          dark
        />
      </div>
      <div className="dashboard-grid">
        <Card
          title="Evolução da receita"
          subtitle="Receita bruta e após deduções, em reais"
        >
          <div className="chart-meta">
            <strong>{brl(s.gross)}</strong>
            <span>no horizonte de 12 meses</span>
          </div>
          <MoneyChart data={r.months} />
        </Card>
        <Card
          title="A leitura do cenário"
          subtitle={`Estratégia ${r.strategy} · ${names[r.strategy]}`}
        >
          <div className="insight-icon">
            <TrendingDown size={25} />
          </div>
          <h3 className="insight-title">
            {s.flow < 0
              ? "Validar antes de escalar."
              : "Resultado positivo nas hipóteses."}
          </h3>
          <p className="body-copy">
            {s.flow < 0
              ? "A contribuição projetada não cobre o plano de custos. Investir em aquisição exige primeiro validar conversão, atividade e disposição a pagar."
              : "Este resultado é condicional. Valide as premissas com pesquisa e experimentos antes de ampliar investimentos."}
          </p>
          <div className="insight-row">
            <span>Contribuição recuperável / adquirido</span>
            <strong>{brl(s.recoverable_contribution)}</strong>
          </div>
          <div className="insight-row">
            <span>Custo de aquisição / jogador</span>
            <strong>{brl(s.cac)}</strong>
          </div>
          <Link className="text-link" to="/financas">
            Analisar a viabilidade <ArrowUpRight size={16} />
          </Link>
        </Card>
      </div>
      <div className="three-grid">
        <Card
          title="Composição dos custos"
          subtitle="Onde os recursos são alocados"
        >
          <CostComposition result={r} />
        </Card>
        <Card
          title="Jogadores em atividade"
          subtitle="Aquisição e atividade mensal hipotéticas"
        >
          <div className="mini-stat">
            {number(r.months[11].active)}
            <span>ativos em M12</span>
          </div>
          <Bars
            data={r.months.map((m) => ({
              name: `M${m.month}`,
              active: m.active,
              new: m.new,
            }))}
            keys={[
              ["active", "Ativos"],
              ["new", "Adquiridos"],
            ]}
            currency={false}
          />
        </Card>
        <Card title="Saúde do caixa" subtitle="Capital e reserva protegida">
          <div className="cash-indicator">
            <CircleDashed size={45} />
            <div>
              <strong>
                {s.insufficient_month
                  ? `Atenção em M${s.insufficient_month}`
                  : "Reserva preservada"}
              </strong>
              <span>Disponibilidade para operação</span>
            </div>
          </div>
          <div className="insight-row">
            <span>Capital inicial</span>
            <strong>{brl(r.parameters.capital)}</strong>
          </div>
          <div className="insight-row">
            <span>Reserva protegida</span>
            <strong>{brl(s.reserve)}</strong>
          </div>
          <div className="insight-row">
            <span>Caixa ao final de M12</span>
            <strong>{brl(s.cash)}</strong>
          </div>
          <p className="fine-print">
            A reserva é uma restrição de disponibilidade. Não representa uma
            despesa.
          </p>
          <Link to="/simulador" className="button full">
            Explorar outro cenário <ArrowRight size={15} />
          </Link>
        </Card>
      </div>
      <ExtendedMetrics result={r} />
      <Notice>
        Modelo heurístico com premissas sintéticas. A consistência matemática
        não comprova a validade comercial das hipóteses.{" "}
        <Link to="/metodologia">Entenda a metodologia.</Link>
      </Notice>
    </>
  );
}
function CostComposition({ result: r }: { result: Result }) {
  const s = r.summary;
  return (
    <div className="cost-list">
      {[
        ["marketing", "Aquisição de jogadores"],
        ["operations", "Operação"],
        ["production", "Produção inicial"],
        ["content", "Atualizações de conteúdo"],
        ["variable", "Entrega e atendimento"],
      ].map(([key, label], i) => (
        <div key={key}>
          <div className="cost-label">
            <span>
              <i
                style={{
                  background: [
                    "#252a26",
                    "#626c63",
                    "#909990",
                    "#b5bdb5",
                    "#d5dbd5",
                  ][i],
                }}
              />
              {label}
            </span>
            <strong>{brl(s[key])}</strong>
          </div>
          <div className="track">
            <span
              style={{
                width: `${s.costs > 0 ? (Number(s[key]) / s.costs) * 100 : 0}%`,
                background: i ? "#a1aaa1" : "#303a31",
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

export function Strategies() {
  const { result: r } = useApp();
  const q = useQuery({
    queryKey: ["comparison"],
    queryFn: () =>
      api<(Summary & { strategy: "A" | "B" | "C"; scenario: string })[]>(
        "/comparison",
      ),
  });
  if (q.isPending) return <Loading />;
  if (q.isError) return <Notice error>{q.error.message}</Notice>;
  const rows = q.data.filter((x) => x.scenario === r.scenario);
  return (
    <>
      <Notice>
        A comparação abaixo usa as premissas oficiais de cada cenário. Maior
        receita não implica maior rentabilidade.
      </Notice>
      <div className="three-grid strategy-cards">
        {rows.map((x) => (
          <Card key={x.strategy}>
            <span className="strategy-letter">{x.strategy}</span>
            <h2>{names[x.strategy]}</h2>
            <p className="body-copy">
              {x.strategy === "A"
                ? "Traje, efeito visual e coleção. Menor investimento inicial; portfólio mais restrito."
                : x.strategy === "B"
                  ? "Passe e efeito visual. Exige entrega periódica de conteúdo e compromisso com a temporada."
                  : "Cinco categorias disponíveis. Amplia o portfólio e também os custos e a substituição entre ofertas."}
            </p>
            <div className="insight-row">
              <span>Receita bruta</span>
              <strong>{brl(x.gross)}</strong>
            </div>
            <div className="insight-row">
              <span>Custos totais</span>
              <strong>{brl(x.costs)}</strong>
            </div>
            <div className="insight-row">
              <span>Contribuição antes de CAC e fixos</span>
              <strong>{brl(x.contribution)}</strong>
            </div>
            <div className="strategy-result">
              <span>Resultado em 12 meses</span>
              <strong>{brl(x.flow)}</strong>
            </div>
          </Card>
        ))}
      </div>
      <div className="two-grid">
        <Card
          title="Faturamento e resultado"
          subtitle={`Cenário ${r.scenario} · premissas oficiais`}
        >
          <Bars
            data={rows.map((x) => ({
              ...x,
              name: `${x.strategy} · ${names[x.strategy]}`,
            }))}
            keys={[
              ["gross", "Receita bruta"],
              ["flow", "Resultado"],
            ]}
          />
        </Card>
        <Card
          title="Doze combinações, uma base auditável"
          subtitle="Quatro cenários por estratégia"
        >
          <DataTable
            rows={q.data}
            columns={[
              { key: "strategy", label: "Estratégia" },
              { key: "scenario", label: "Cenário" },
              { key: "gross", label: "Receita", render: (v) => brl(Number(v)) },
              {
                key: "flow",
                label: "Resultado",
                render: (v) => brl(Number(v)),
              },
            ]}
            searchable
          />
        </Card>
      </div>
      <Notice>
        As cestas são mutuamente exclusivas por jogador ativo-mês. Novos
        produtos disputam a escolha com os demais produtos e com a opção de não
        compra.
      </Notice>
    </>
  );
}

export function Products() {
  const { result: r, input } = useApp();
  const [factor, setFactor] = useState(1);
  const q = useQuery({
    queryKey: ["price-sensitivity", input, factor],
    queryFn: () =>
      api<Result>("/simulations/preview", "POST", {
        ...input,
        overrides: {
          ...r.parameters,
          price_mult: Object.fromEntries(
            Object.entries(r.parameters.price_mult).map(([k, v]) => [
              k,
              v * factor,
            ]),
          ),
        },
      }),
  });
  return (
    <>
      <div className="two-grid">
        <Card
          title="Portfólio da estratégia"
          subtitle="Valores esperados no horizonte de 12 meses"
        >
          <DataTable
            rows={r.products}
            columns={[
              { key: "name", label: "Produto" },
              { key: "price", label: "Preço", render: (v) => brl(Number(v)) },
              {
                key: "probability",
                label: "Escolha / ativo-mês",
                render: (v) => percent(Number(v)),
              },
              {
                key: "units",
                label: "Unidades",
                render: (v) => number(Number(v)),
              },
              { key: "gross", label: "Receita", render: (v) => brl(Number(v)) },
            ]}
          />
        </Card>
        <Card
          title="A alternativa de não comprar"
          subtitle="Modelo de escolha com opção externa"
        >
          <div className="large-stat">{percent(r.none_probability)}</div>
          <p className="body-copy">
            Probabilidade hipotética de não escolher nenhuma cesta disponível no
            mês. As probabilidades de compra e não compra somam 100%.
          </p>
          <Notice>
            Os parâmetros representam atratividade assumida. O modelo não é um
            logit multinomial estimado com dados observados.
          </Notice>
        </Card>
      </div>
      <Card
        title="Sensibilidade conjunta de preços"
        subtitle="Modifique todos os preços disponíveis, mantendo os demais parâmetros"
      >
        <div className="range-row">
          <label htmlFor="price-factor">
            Multiplicador de preços <strong>{percent(factor)}</strong>
          </label>
          <input
            id="price-factor"
            type="range"
            min="0.85"
            max="1.15"
            step="0.05"
            value={factor}
            onChange={(e) => setFactor(+e.target.value)}
          />
          <span>
            Candidatos: −15%, referência e +15%. A resposta de demanda é
            heurística.
          </span>
        </div>
        {q.isPending ? (
          <Loading />
        ) : q.isError ? (
          <Notice error>{q.error.message}</Notice>
        ) : (
          <div className="metrics compact-metrics">
            <Metric
              label="Receita projetada"
              value={brl(q.data.summary.gross)}
              note="Execução Python com novos preços"
              help="Demanda é recalculada com a mesma opção externa."
            />
            <Metric
              label="Escolha de compra"
              value={percent(1 - q.data.none_probability)}
              note="Por jogador ativo-mês"
              help="Cestas exclusivas; não é conversão observada."
            />
            <Metric
              label="Efeito na receita"
              value={brl(q.data.summary.gross - r.summary.gross)}
              note="Diferença frente à seleção atual"
              help="O resultado é condicional à sensibilidade assumida."
            />
          </div>
        )}
      </Card>
      <Notice>
        Aumentar o preço de um item reduz seu peso relativo e redistribui
        escolha para os outros itens e a não compra. Use o simulador para
        alterar preços individuais e atratividade.
      </Notice>
    </>
  );
}

export function Cohorts() {
  const { result: r } = useApp();
  return (
    <>
      <div className="metrics">
        <Metric
          label="Jogadores adquiridos"
          value={number(r.summary.acquired)}
          note="Soma de novas contas no horizonte"
          help="Coortes de aquisição distintas. Volume mensal × 12."
        />
        <Metric
          label="Jogadores-mês ativos"
          value={number(r.summary.active_player_months)}
          note="Atividade somada; não são pessoas únicas"
          help="Cada coorte contribui conforme a curva mensal e sua idade."
        />
        <Metric
          label="LTV parcial da coorte M1"
          value={brl(r.summary.ltv_partial)}
          note="Contribuição por adquirido · 12 meses"
          help="Receita após deduções menos custo variável, dividida pelos adquiridos. Exclui CAC e fixos."
        />
        <Metric
          label="CAC por adquirido"
          value={brl(r.summary.cac)}
          note="Aquisição paga assumida"
          help="Marketing é volume adquirido × CAC; escala amplia o gasto de aquisição."
        />
      </div>
      <div className="two-grid">
        <Card
          title="Curva de atividade mensal"
          subtitle="Probabilidade hipotética de atividade por idade da coorte"
        >
          <Bars
            data={r.parameters.activity.map((v, i) => ({
              name: `M${i}`,
              active: v * 100,
            }))}
            keys={[["active", "Atividade (%)"]]}
            currency={false}
          />
        </Card>
        <Card title="Retenção diária">
          <h3>D1, D7 e D30</h3>
          <p className="body-copy">
            Não disponível para este conjunto de dados.
          </p>
          <Notice>
            A curva descreve atividade em qualquer dia de cada mês. Eventos
            diários seriam necessários para calcular retenção em dias exatos.
          </Notice>
          <div className="insight-row">
            <span>ARPU bruto / jogador-mês ativo</span>
            <strong>{brl(r.summary.arpu)}</strong>
          </div>
          <div className="insight-row">
            <span>ARPPU bruto / comprador-mês</span>
            <strong>{brl(r.summary.arppu)}</strong>
          </div>
        </Card>
      </div>
      <Card
        title="Contribuição das coortes"
        subtitle="Horizontes diferentes: as coortes recentes ainda não completaram 12 meses"
      >
        <DataTable<Cohort>
          rows={r.cohorts}
          columns={[
            { key: "cohort_month", label: "Coorte", render: (v) => `M${v}` },
            { key: "horizon_months", label: "Meses observados" },
            {
              key: "acquired",
              label: "Adquiridos",
              render: (v) => number(Number(v)),
            },
            {
              key: "active_player_months",
              label: "Jogadores-mês",
              render: (v) => number(Number(v)),
            },
            {
              key: "contribution_per_acquired",
              label: "LTV parcial",
              render: (v) => brl(Number(v)),
            },
            { key: "CAC", label: "CAC", render: (v) => brl(Number(v)) },
            {
              key: "net_after_CAC",
              label: "Contribuição após CAC",
              render: (v) => brl(Number(v)),
            },
          ]}
        />
      </Card>
    </>
  );
}

export function Finances() {
  const { result: r, input } = useApp();
  const q = useQuery({
    queryKey: ["sensitivity", input],
    queryFn: () =>
      api<{ name: string; lower: number; upper: number }[]>(
        "/sensitivity",
        "POST",
        input,
      ),
  });
  const s = r.summary;
  return (
    <>
      <div className="metrics">
        <Metric
          label="Resultado acumulado"
          value={brl(s.flow)}
          note="DRE de M1 a M12"
          help="Receita após deduções menos todos os custos, sem capital inicial."
          dark
        />
        <Metric
          label="Caixa final"
          value={brl(s.cash)}
          note="Inclui capital inicial"
          help="Capital inicial mais fluxos mensais. O modelo assume recebimento no mesmo mês."
        />
        <Metric
          label="Insuficiência da reserva"
          value={
            s.insufficient_month ? `Mês ${s.insufficient_month}` : "Não ocorre"
          }
          note="Primeiro mês abaixo da reserva"
          help="Caixa disponível menos reserva protegida < 0."
        />
        <Metric
          label="CAC máximo após fixos"
          value={brl(s.max_cac_after_fixed)}
          note="Limite médio no horizonte completo"
          help="(Contribuição menos operação, produção e conteúdo) ÷ adquiridos. Negativo indica déficit mesmo sem mídia."
        />
      </div>
      <div className="two-grid">
        <Card
          title="Fluxo de caixa"
          subtitle="Saldo e disponibilidade após reserva"
        >
          <MoneyChart
            data={r.months}
            lines={[
              ["cash", "Caixa"],
              ["usable_cash", "Disponível após reserva"],
            ]}
          />
        </Card>
        <Card
          title="Ponto de equilíbrio"
          subtitle="Escala e recuperação de aquisição"
        >
          <div className="large-stat">
            {s.break_even_acquired
              ? number(s.break_even_acquired)
              : "Inviável por escala"}
          </div>
          <p className="body-copy">
            {s.break_even_acquired
              ? "Contas adquiridas necessárias sob contribuição unitária e CAC constantes. O gasto de mídia aumenta com as contas."
              : "A contribuição média por adquirido é menor ou igual ao CAC. Ampliar a aquisição amplia o déficit, sob estas premissas."}
          </p>
          <div className="insight-row">
            <span>Base equivalente de jogadores-mês ativos</span>
            <strong>{number(s.break_even_active_months)}</strong>
          </div>
          <p className="fine-print">
            Equivalência contábil mantendo o orçamento de mídia atual. Não
            representa jogadores únicos nem um plano de crescimento com
            aquisição gratuita.
          </p>
          <div className="insight-row">
            <span>Primeiro mês de caixa negativo</span>
            <strong>
              {s.cash_negative_month
                ? `M${s.cash_negative_month}`
                : "Não ocorre"}
            </strong>
          </div>
        </Card>
      </div>
      <div className="two-grid">
        <Card
          title="Receita e deduções"
          subtitle="Reconciliação até a receita disponível"
        >
          <Waterfall summary={s} />
          <div className="waterfall">
            {[
              ["gross", "Receita bruta"],
              ["refunds", "− Reembolsos"],
              ["platform", "− Plataforma"],
              ["tax", "− Tributos"],
              ["net", "= Após deduções"],
            ].map(([k, label]) => (
              <div className="insight-row" key={k}>
                <span>{label}</span>
                <strong>{brl(s[k])}</strong>
              </div>
            ))}
          </div>
        </Card>
        <Card
          title="Sensibilidade do resultado"
          subtitle="Variação de −15% e +15% · demais hipóteses constantes"
        >
          {q.isPending ? (
            <Loading />
          ) : q.isError ? (
            <Notice error>{q.error.message}</Notice>
          ) : (
            <div className="tornado">
              {[...q.data]
                .sort(
                  (a, b) =>
                    Math.max(Math.abs(b.lower), Math.abs(b.upper)) -
                    Math.max(Math.abs(a.lower), Math.abs(a.upper)),
                )
                .map((x) => (
                  <div key={x.name}>
                    <strong>{x.name}</strong>
                    <div className="tornado-values">
                      <span>{brl(x.lower)}</span>
                      <span>{brl(x.upper)}</span>
                    </div>
                    <div className="tornado-bars">
                      <i
                        style={{
                          width: `${(Math.abs(x.lower) / Math.max(...q.data.flatMap((x) => [Math.abs(x.lower), Math.abs(x.upper)]), 1)) * 50}%`,
                        }}
                      />
                      <i
                        style={{
                          width: `${(Math.abs(x.upper) / Math.max(...q.data.flatMap((x) => [Math.abs(x.lower), Math.abs(x.upper)]), 1)) * 50}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
            </div>
          )}
        </Card>
      </div>
      <Card
        title="Resultado mensal e acumulado"
        subtitle="Resultado acumulado exclui o capital inicial"
      >
        <MoneyChart
          data={r.months}
          lines={[
            ["flow", "Resultado mensal"],
            ["cumulative_flow", "Acumulado"],
          ]}
        />
      </Card>
      <Card
        title="DRE gerencial mensal"
        subtitle="Valores em reais; totais calculados antes do arredondamento de exibição"
      >
        <DataTable<Month>
          rows={r.months}
          columns={[
            { key: "month", label: "Mês", render: (v) => `M${v}` },
            ...(
              [
                ["gross", "Receita bruta"],
                ["refunds", "Reembolsos"],
                ["platform", "Plataforma"],
                ["tax", "Tributos"],
                ["net", "Líquido"],
                ["variable", "Variáveis"],
                ["production", "Produção"],
                ["content", "Conteúdo"],
                ["operations", "Operação"],
                ["marketing", "Aquisição"],
                ["flow", "Resultado"],
                ["cash", "Caixa"],
              ] as const
            ).map(([key, label]) => ({
              key,
              label,
              render: (v: Month[keyof Month]) => brl(Number(v)),
            })),
          ]}
        />
      </Card>
    </>
  );
}

export function Benchmarks() {
  const q = useQuery({
    queryKey: ["benchmarks"],
    queryFn: () => api<Benchmark[]>("/benchmarks"),
  });
  if (q.isPending) return <Loading />;
  if (q.isError) return <Notice error>{q.error.message}</Notice>;
  return (
    <>
      <Notice>
        Preços históricos registrados no estudo em 29/10/2026. Não foram
        reconfirmados por esta aplicação. Recargas de moeda virtual não
        equivalem ao preço de cosméticos individuais.
      </Notice>
      <Card
        title="Ofertas documentadas"
        subtitle="Fonte, canal e data acompanham cada valor"
      >
        <DataTable<Benchmark>
          rows={q.data}
          columns={[
            { key: "game", label: "Jogo" },
            { key: "product", label: "Oferta" },
            { key: "offer_type", label: "Tipo" },
            {
              key: "price",
              label: "Preço (BRL)",
              render: (v) => brl(Number(v)),
            },
            { key: "channel", label: "Canal" },
            {
              key: "consulted_at",
              label: "Consulta",
              render: (v) =>
                new Date(String(v) + "T12:00:00").toLocaleDateString("pt-BR"),
            },
            { key: "verification_status", label: "Status" },
            {
              key: "source_url",
              label: "Fonte",
              render: (v) => (
                <a
                  className="text-link"
                  href={String(v)}
                  target="_blank"
                  rel="noreferrer"
                >
                  Consultar <ExternalLink size={12} />
                </a>
              ),
            },
            { key: "limitations", label: "Limitações" },
          ]}
          searchable
        />
      </Card>
    </>
  );
}

export function Reports() {
  const { input, result: r, notify } = useApp();
  const [busy, setBusy] = useState(false);
  const exportFile = async (format: "csv" | "pdf", dataset: string) => {
    setBusy(true);
    try {
      await download(input, format, dataset);
      notify("Arquivo exportado com sucesso.");
    } catch (e) {
      notify((e as Error).message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <>
      <Notice>
        Seleção ativa: estratégia {r.strategy}, cenário {r.scenario}
        {input.overrides ? " personalizado" : ""}. CSVs e PDFs usam a mesma
        execução da interface. A comparação de estratégias exporta as 12
        combinações oficiais.
      </Notice>
      <div className="three-grid">
        {[
          [
            "months",
            "Projeções financeiras",
            "DRE e fluxo de caixa dos 12 meses.",
          ],
          [
            "comparison",
            "Comparação de estratégias",
            "As três estratégias nos quatro cenários oficiais.",
          ],
          [
            "cohorts",
            "Dados de coortes",
            "Atividade, contribuição e LTV parcial.",
          ],
          [
            "products",
            "Resultados por produto",
            "Preço, escolha, unidades e receita projetada.",
          ],
        ].map(([key, title, desc]) => (
          <Card key={key} title={title}>
            <p className="body-copy">{desc}</p>
            <button
              className="button"
              disabled={busy}
              onClick={() => exportFile("csv", key)}
            >
              Baixar CSV <ArrowUpRight size={14} />
            </button>
          </Card>
        ))}
        <Card title="Relatório de simulação">
          <p className="body-copy">
            Projeção mensal, versão do modelo e todas as hipóteses utilizadas.
          </p>
          <button
            className="button primary"
            disabled={busy}
            onClick={() => exportFile("pdf", "months")}
          >
            Gerar PDF <ArrowUpRight size={14} />
          </button>
        </Card>
      </div>
    </>
  );
}

export function Methodology() {
  return (
    <div className="methodology">
      <Card title="Decisões orientadas por hipóteses explícitas">
        <p>
          Datavoxen transforma o estudo independente de Ilhas de Órion, do
          fictício Estúdio Horizonte, em uma ferramenta de análise. Os dados
          comerciais são sintéticos. Benchmarks documentam ofertas anunciadas;
          não medem a demanda pelo produto fictício.
        </p>
        <blockquote>
          Não é possível comprovar a conversão, a retenção ou a disposição a
          pagar de jogadores de um produto fictício sem realizar pesquisa ou
          experimento real.
        </blockquote>
        <p>
          A consistência matemática do modelo não comprova a validade empírica
          das premissas comerciais.
        </p>
      </Card>
      <div className="two-grid">
        <Card title="Escolha e precificação">
          <p>
            Para cada produto, peso = atratividade ÷ probabilidade externa de
            referência × engajamento × (preço / preço de referência)
            <sup>−sensibilidade</sup>.
          </p>
          <p>
            Probabilidade de compra = peso ÷ (1 + soma dos pesos). A não compra
            tem probabilidade 1 ÷ (1 + soma dos pesos).
          </p>
          <p>
            São cestas mutuamente exclusivas por jogador ativo-mês. Não há
            compras múltiplas nem parâmetros estimados com dados transacionais.
          </p>
        </Card>
        <Card title="Receita, contribuição e caixa">
          <p>
            Receita bruta = unidades esperadas × preço × fator de gasto.
            Reembolso incide no bruto; plataforma e tributos usam a base após
            reembolso.
          </p>
          <p>
            Contribuição = receita após deduções − custos variáveis. Resultado =
            contribuição − produção − conteúdo − operação − aquisição.
          </p>
          <p>
            Caixa = capital inicial + resultados acumulados. A reserva é
            protegida, sem virar despesa. O modelo assume repasse no mesmo mês.
          </p>
        </Card>
        <Card title="Jogadores e denominadores">
          <p>
            Ativos mensais somam a atividade de cada coorte conforme sua idade.
            Jogadores-mês ativos contam oportunidades mensais, não pessoas
            únicas.
          </p>
          <p>
            ARPU = receita bruta ÷ jogadores-mês ativos. ARPPU = receita bruta ÷
            compradores-mês. LTV parcial = contribuição da coorte ÷ adquiridos
            na janela disponível.
          </p>
          <p>
            D1, D7 e D30 exigem eventos diários. Coortes recentes têm horizontes
            menores; não compare maturidades como se fossem iguais.
          </p>
        </Card>
        <Card title="Reprodução e limites">
          <p>
            Motor original e premissas do ZIP são a referência numérica. Os 12
            resultados de cenário e cada linha mensal têm regressão
            automatizada. Valores monetários usam HALF_UP a dois decimais na
            saída; os cálculos mantêm a precisão do motor original.
          </p>
          <p>
            O fator de gasto do código original altera receita, sem alterar
            unidades ou custos variáveis. O parâmetro legado “init” não é
            utilizado pelo original. Ambos estão documentados na auditoria.
          </p>
          <p>
            Preços, custos, atividade e CAC não são evidência de mercado. A
            identidade visual usa as duas referências fornecidas pela
            proprietária: painéis monocromáticos com cartões arredondados,
            navegação em cápsulas e contraste preto e branco.
          </p>
        </Card>
      </div>
      <Card title="Fontes do estudo">
        <p><Link className="text-link" to="/estudo">Abrir o acervo público: PDF original, SQLite, CSVs e modelo Python <ArrowUpRight size={14}/></Link></p>
        <p>
          Documentos originais preservados em docs/references: relatório
          encerrado de 2026, modelo Python, premissas, projeções, coortes,
          sensibilidade e registro de fontes.
        </p>
        <p>
          Benchmarks: App Store Brasil, loja oficial COD Mobile e Codashop. Cada
          oferta possui seu link na seção Benchmarking. Nenhuma atualização
          automática é executada.
        </p>
        <p>
          Modelo 2026.1 · horizonte fixo de 12 meses · produção inicial em M1 ·
          conteúdo em M4, M7 e M10.
        </p>
      </Card>
    </div>
  );
}
