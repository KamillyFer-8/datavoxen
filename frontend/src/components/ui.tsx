import { useState, type ReactNode } from "react";
import {
  Info,
  ArrowDownToLine,
  ChevronLeft,
  ChevronRight,
  type LucideIcon,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
  BarChart,
  Bar,
} from "recharts";
export const brl = (value: number | null | undefined) =>
  value == null
    ? "Não disponível"
    : new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL",
      }).format(value);
export const number = (value: number | null | undefined) =>
  value == null
    ? "—"
    : new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 }).format(
        value,
      );
export const percent = (value: number) =>
  new Intl.NumberFormat("pt-BR", {
    style: "percent",
    maximumFractionDigits: 2,
  }).format(value);
export const compact = (value: number) =>
  new Intl.NumberFormat("pt-BR", {
    notation: "compact",
    maximumFractionDigits: 0,
  }).format(value);
export function Card({
  title,
  subtitle,
  children,
  className = "",
}: {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`card ${className}`}>
      {title && (
        <div className="card-heading">
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
      )}
      {children}
    </section>
  );
}
export function Metric({
  label,
  value,
  note,
  help,
  dark = false,
  icon: Icon,
}: {
  label: string;
  value: string;
  note: string;
  help: string;
  dark?: boolean;
  icon?: LucideIcon;
}) {
  return (
    <div className={`metric ${dark ? "dark" : ""}`}>
      {Icon && (
        <div className="metric-icon" aria-hidden="true">
          <Icon size={19} strokeWidth={1.6} />
        </div>
      )}
      <div className="metric-label">
        {label}
        <details className="help">
          <summary aria-label={`Explicação: ${label}`}>
            <Info size={14} />
          </summary>
          <p>{help}</p>
        </details>
      </div>
      <strong>{value}</strong>
      <span>{note}</span>
    </div>
  );
}
export function Notice({
  children,
  error = false,
}: {
  children: ReactNode;
  error?: boolean;
}) {
  return (
    <div
      className={`notice ${error ? "error" : ""}`}
      role={error ? "alert" : "status"}
    >
      <Info size={17} />
      <div>{children}</div>
    </div>
  );
}
export function Loading() {
  return (
    <div className="loading" role="status">
      <span className="spinner" />
      Consultando o motor financeiro…
    </div>
  );
}
export function Waterfall({
  summary: s,
}: {
  summary: Record<string, number | null>;
}) {
  const data = [
    { name: "Bruto", base: 0, value: s.gross },
    {
      name: "Reembolso",
      base: Number(s.gross) - Number(s.refunds),
      value: s.refunds,
    },
    {
      name: "Plataforma",
      base: Number(s.net) + Number(s.tax),
      value: s.platform,
    },
    { name: "Tributos", base: s.net, value: s.tax },
    { name: "Disponível", base: 0, value: s.net },
  ];
  return (
    <div
      className="chart"
      role="img"
      aria-label="Cascata de receita e deduções"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid vertical={false} stroke="#eee" />
          <XAxis
            dataKey="name"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 10 }}
          />
          <YAxis
            tickFormatter={compact}
            width={60}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 10 }}
          />
          <Tooltip
            formatter={(v, name) => (name === "Base" ? null : brl(Number(v)))}
          />
          <Bar
            name="Base"
            dataKey="base"
            stackId="a"
            fill="transparent"
            isAnimationActive={false}
          />
          <Bar
            name="Parcela"
            dataKey="value"
            stackId="a"
            fill="#606060"
            radius={[4, 4, 0, 0]}
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
export function MoneyChart({
  data,
  lines = [
    ["gross", "Receita bruta"],
    ["net", "Após deduções"],
  ],
}: {
  data: Record<string, unknown>[];
  lines?: string[][];
}) {
  return (
    <div
      className="chart"
      role="img"
      aria-label={lines.map((l) => l[1]).join(" e ")}
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 15, right: 12, bottom: 0, left: 0 }}
        >
          <defs>
            <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#777" stopOpacity={0.16} />
              <stop offset="100%" stopColor="#777" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            vertical={false}
            stroke="#eaeae8"
            strokeDasharray="3 4"
          />
          <XAxis
            dataKey="month"
            tickFormatter={(v) => `M${v}`}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#888" }}
          />
          <YAxis
            tickFormatter={compact}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11, fill: "#888" }}
            width={60}
          />
          <Tooltip
            formatter={(v) => brl(Number(v))}
            labelFormatter={(v) => `Mês ${v}`}
            contentStyle={{ borderRadius: 14, border: "1px solid #eee" }}
          />
          <Legend
            iconType="circle"
            iconSize={6}
            wrapperStyle={{ fontSize: 11, paddingTop: 20 }}
          />
          {lines.map(([key, label], i) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              name={label}
              stroke={i ? "#a6aaa6" : "#222"}
              strokeDasharray={i ? "4 4" : undefined}
              fill={i ? "transparent" : "url(#fill)"}
              strokeWidth={2}
              isAnimationActive={false}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
export function Bars({
  data,
  keys,
  x = "name",
  currency = true,
}: {
  data: Record<string, unknown>[];
  keys: string[][];
  x?: string;
  currency?: boolean;
}) {
  return (
    <div className="chart">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 16, left: 0, right: 12 }}>
          <CartesianGrid vertical={false} stroke="#eee" />
          <XAxis
            dataKey={x}
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            tickFormatter={compact}
            axisLine={false}
            tickLine={false}
            width={65}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            formatter={(v) => (currency ? brl(Number(v)) : number(Number(v)))}
          />
          <Legend iconSize={7} wrapperStyle={{ fontSize: 11 }} />
          {keys.map(([key, label], i) => (
            <Bar
              key={key}
              dataKey={key}
              name={label}
              fill={i ? "#bfc3bd" : "#272b28"}
              radius={[5, 5, 0, 0]}
              isAnimationActive={false}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
export type Column<T> = {
  key: keyof T;
  label: string;
  render?: (value: T[keyof T], row: T) => ReactNode;
};
export function DataTable<T extends object>({
  rows,
  columns,
  searchable = false,
}: {
  rows: T[];
  columns: Column<T>[];
  searchable?: boolean;
}) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(0);
  const [sort, setSort] = useState<{ key: keyof T; asc: boolean } | null>(null);
  const filtered = rows.filter((r) =>
    Object.values(r)
      .join(" ")
      .toLocaleLowerCase("pt-BR")
      .includes(search.toLocaleLowerCase("pt-BR")),
  );
  const sorted = sort
    ? [...filtered].sort((a, b) => {
        const av = a[sort.key],
          bv = b[sort.key];
        return (
          (typeof av === "number" && typeof bv === "number"
            ? av - bv
            : String(av).localeCompare(String(bv), "pt-BR")) *
          (sort.asc ? 1 : -1)
        );
      })
    : filtered;
  const current = Math.min(page, Math.max(0, Math.ceil(sorted.length / 8) - 1));
  return (
    <>
      {searchable && (
        <input
          className="table-search"
          aria-label="Filtrar tabela"
          placeholder="Buscar nesta tabela…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
        />
      )}
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              {columns.map((c) => (
                <th
                  key={String(c.key)}
                  aria-sort={
                    sort?.key === c.key
                      ? sort.asc
                        ? "ascending"
                        : "descending"
                      : "none"
                  }
                >
                  <button
                    onClick={() =>
                      setSort({
                        key: c.key,
                        asc: sort?.key === c.key ? !sort.asc : true,
                      })
                    }
                  >
                    {c.label} ↕
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.slice(current * 8, current * 8 + 8).map((row, i) => (
              <tr key={i}>
                {columns.map((c) => (
                  <td key={String(c.key)}>
                    {c.render
                      ? c.render(row[c.key], row)
                      : String(row[c.key] ?? "—")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {!sorted.length && <p className="empty">Nenhum registro encontrado.</p>}
      </div>
      <div className="pagination">
        <span>
          {sorted.length} registros · Página {current + 1} de{" "}
          {Math.max(1, Math.ceil(sorted.length / 8))}
        </span>
        <div>
          <button
            aria-label="Página anterior"
            disabled={current === 0}
            onClick={() => setPage(current - 1)}
          >
            <ChevronLeft size={16} />
          </button>
          <button
            aria-label="Próxima página"
            disabled={(current + 1) * 8 >= sorted.length}
            onClick={() => setPage(current + 1)}
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </>
  );
}
export function ExportButton({
  onClick,
  label = "Exportar relatório",
}: {
  onClick: () => void;
  label?: string;
}) {
  return (
    <button className="button" onClick={onClick}>
      <ArrowDownToLine size={15} />
      {label}
    </button>
  );
}
