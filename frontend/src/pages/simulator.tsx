import { useEffect, useRef, useState } from "react";
import { useForm, type Path } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight, RotateCcw, Save, Upload, Download } from "lucide-react";
import { useApp } from "../main";
import { api, download, downloadConfig } from "../services/api";
import { brl, Card, Loading, Metric, Notice } from "../components/ui";
import type { Parameters, ProductKey, Result } from "../types";

const products = {
  traje: "Traje cosmético",
  efeito: "Efeito visual",
  colecao: "Coleção temática",
  passe: "Passe de temporada",
  sazonal: "Oferta sazonal",
};
const keys = z.enum(["traje", "efeito", "colecao", "passe", "sazonal"]);
const positive = z.number().finite().min(0).max(1e9);
const rate = z.number().finite().min(0).max(1);
const schema = z
  .object({
    cac: positive,
    acq: z.number().int().min(1).max(1000000),
    eng: z.number().min(0).max(100),
    spend: z.number().min(0).max(10),
    opex: z.number().min(0).max(10),
    elasticity: z.number().min(0).max(5),
    price_mult: z.record(keys, z.number().min(0.05).max(10)),
    activity: z.array(rate).length(12),
    capital: positive,
    reserve: positive,
    fee: rate,
    tax: rate,
    refund: rate,
    operations: positive,
    production: positive,
    content: positive,
    unit_cost: z.record(keys, positive),
    attractiveness: z.record(keys, rate),
  })
  .refine((p) => p.reserve <= p.capital, {
    message: "A reserva não pode exceder o capital.",
    path: ["reserve"],
  })
  .refine((p) => p.fee + p.tax <= 1, {
    message: "Tarifas e tributos excedem 100%.",
    path: ["fee"],
  })
  .refine(
    (p) => Object.values(p.attractiveness).reduce((a, b) => a + b, 0) < 1,
    {
      message: "Atratividade total deve ser menor que 100%.",
      path: ["attractiveness"],
    },
  );

export function Simulator() {
  const { result: r, input, setInput, notify } = useApp();
  const [name, setName] = useState(input.name || "Minha simulação");
  const [saving, setSaving] = useState(false);
  const importRef = useRef<HTMLInputElement>(null);
  const original = useQuery({
    queryKey: ["baseline", input.strategy, input.scenario],
    queryFn: () =>
      api<Result>(
        `/reference?strategy=${input.strategy}&scenario=${input.scenario}`,
      ),
  });
  const form = useForm<Parameters>({
    resolver: zodResolver(schema),
    defaultValues: r.parameters,
  });
  const { reset } = form;
  useEffect(() => { reset(r.parameters); }, [r.parameters, reset]);
  useEffect(() => { setName(input.name || "Minha simulação"); }, [input.name]);
  const field = (name: Path<Parameters>, label: string, step = "any") => (
    <label className="field" key={name}>
      {label}
      <input
        type="number"
        step={step}
        {...form.register(name, { valueAsNumber: true })}
      />
    </label>
  );
  const save = () => {
    downloadConfig(
      { ...input, name },
      r.parameters,
      r.model_version,
      r.model_hash,
    );
    notify(
      "Hipóteses exportadas. O arquivo pode ser importado para recuperar esta análise.",
    );
  };
  const importConfig = async (file: File | undefined) => {
    if (!file) return;
    setSaving(true);
    try {
      if (file.size > 100000)
        throw new Error("O arquivo de hipóteses deve ter até 100 KB.");
      const data = JSON.parse(await file.text());
      if (!data || typeof data !== "object" || Array.isArray(data))
        throw new Error("Arquivo de hipóteses inválido.");
      if (
        data.model_version !== r.model_version ||
        data.model_hash !== r.model_hash
      )
        throw new Error("O arquivo pertence a outra versão do modelo.");
      const candidate = {
        strategy: data.strategy,
        scenario: data.scenario,
        name: data.name,
        overrides: data.overrides,
      };
      if (!candidate.overrides || typeof candidate.overrides !== "object")
        throw new Error("Arquivo de hipóteses inválido.");
      const checked = await api<Result>(
        "/simulations/preview",
        "POST",
        candidate,
      );
      setInput({
        ...candidate,
        strategy: checked.strategy,
        scenario: checked.scenario,
        overrides: checked.parameters,
      });
      setName(candidate.name || "Minha simulação");
      notify("Hipóteses importadas e recalculadas pelo motor Python.");
    } catch (error) {
      notify(
        error instanceof SyntaxError
          ? "O arquivo não contém um JSON válido."
          : (error as Error).message,
      );
    } finally {
      setSaving(false);
      if (importRef.current) importRef.current.value = "";
    }
  };
  const exportCsv = async () => {
    try {
      await download({ ...input, name }, "csv");
      notify("Resultado exportado em CSV.");
    } catch (error) {
      notify((error as Error).message);
    }
  };
  return (
    <>
      <Notice>
        O cenário oficial é preservado. Cada execução personalizada usa o motor
        Python e pode ser comparada à referência original.
      </Notice>
      <div className="simulator-layout">
        <form
          onSubmit={form.handleSubmit((values) =>
            setInput({ ...input, name, overrides: values }),
          )}
          noValidate
        >
          <Card
            title="Configure suas hipóteses"
            subtitle="Valores monetários em reais; taxas entre 0 e 1"
          >
            <div className="form-grid">
              {field("acq", "Novos jogadores por mês", "1")}
              {field("cac", "CAC por adquirido")}
              {field("eng", "Multiplicador de atratividade")}
              {field("elasticity", "Sensibilidade de escolha")}
              {field("spend", "Multiplicador de gasto")}
              {field("opex", "Multiplicador operacional")}
            </div>
            <details className="parameter-section" open>
              <summary>Produtos, preços e atratividade</summary>
              <p className="fine-print">
                Fator de preço relativo ao catálogo original. 1 = preço de
                referência. Atratividade é probabilidade de referência assumida.
              </p>
              {Object.entries(products).map(([key, label]) => (
                <fieldset className="product-fields" key={key}>
                  <legend>{label}</legend>
                  <div className="form-grid">
                    {field(`price_mult.${key as ProductKey}`, "Fator de preço")}
                    {field(
                      `attractiveness.${key as ProductKey}`,
                      "Atratividade (0–1)",
                    )}
                    {field(
                      `unit_cost.${key as ProductKey}`,
                      "Custo variável por unidade",
                    )}
                  </div>
                </fieldset>
              ))}
            </details>
            <details className="parameter-section">
              <summary>Operação, produção e deduções</summary>
              <div className="form-grid">
                {field("operations", "Operação mensal")}
                {field("production", "Produção inicial")}
                {field("content", "Conteúdo por atualização")}
                {field("refund", "Reembolso (0–1)")}
                {field("fee", "Plataforma (0–1)")}
                {field("tax", "Tributos (0–1)")}
              </div>
            </details>
            <details className="parameter-section">
              <summary>Curva de atividade mensal</summary>
              <p className="fine-print">
                Probabilidade de atividade por idade da coorte. Não representa
                D1, D7 ou D30.
              </p>
              <div className="form-grid activity-fields">
                {r.parameters.activity.map((_, i) =>
                  field(`activity.${i}`, `M${i} (0–1)`),
                )}
              </div>
            </details>
            <details className="parameter-section">
              <summary>Capital e reserva</summary>
              <div className="form-grid">
                {field("capital", "Capital inicial")}
                {field("reserve", "Reserva protegida")}
              </div>
            </details>
            {Object.keys(form.formState.errors).length > 0 && (
              <Notice error>
                Confira os valores dos campos: taxas e atividade entre 0 e 1,
                preços positivos, aquisição de 1 a 1.000.000 e reserva até o
                capital. Atratividade total deve ser menor que 1.
              </Notice>
            )}
            <div className="form-actions">
              <button
                type="button"
                className="button"
                onClick={() => {
                  if (original.data) {
                    form.reset(original.data.parameters);
                    setInput({
                      strategy: input.strategy,
                      scenario: input.scenario,
                    });
                  }
                }}
              >
                <RotateCcw size={15} />
                Restaurar referência
              </button>
              <button className="button primary" type="submit">
                Executar simulação <ArrowRight size={15} />
              </button>
            </div>
          </Card>
        </form>
        <div className="simulation-summary">
          <Card
            title="Resultado da execução"
            subtitle={
              input.overrides
                ? "Hipóteses personalizadas"
                : "Referência oficial"
            }
          >
            <div className="large-stat">{brl(r.summary.flow)}</div>
            <p className="fine-print">
              Resultado financeiro acumulado em 12 meses
            </p>
            {original.isPending ? (
              <Loading />
            ) : original.isError ? (
              <Notice error>{original.error.message}</Notice>
            ) : (
              <>
                <div className="insight-row">
                  <span>Resultado original</span>
                  <strong>{brl(original.data.summary.flow)}</strong>
                </div>
                <div className="insight-row">
                  <span>Variação do resultado</span>
                  <strong>
                    {brl(r.summary.flow - original.data.summary.flow)}
                  </strong>
                </div>
                <div className="insight-row">
                  <span>Receita modificada</span>
                  <strong>{brl(r.summary.gross)}</strong>
                </div>
                <div className="insight-row">
                  <span>Receita original</span>
                  <strong>{brl(original.data.summary.gross)}</strong>
                </div>
              </>
            )}
            <div className="insight-row">
              <span>Caixa final</span>
              <strong>{brl(r.summary.cash)}</strong>
            </div>
            <div className="insight-row">
              <span>Insuficiência da reserva</span>
              <strong>
                {r.summary.insufficient_month
                  ? `M${r.summary.insufficient_month}`
                  : "Não ocorre"}
              </strong>
            </div>
            <label className="field">
              Nome da simulação
              <input
                value={name}
                maxLength={100}
                onChange={(e) => setName(e.target.value)}
              />
            </label>
            <button
              className="button primary full"
              disabled={saving}
              onClick={save}
            >
              <Save size={15} />
              Baixar hipóteses (JSON)
            </button>
            <button
              className="button full"
              disabled={saving}
              onClick={() => importRef.current?.click()}
            >
              <Upload size={15} />
              {saving ? "Importando…" : "Importar hipóteses"}
            </button>
            <input
              ref={importRef}
              type="file"
              accept=".json,application/json"
              className="file-input"
              aria-label="Arquivo de hipóteses"
              onChange={(event) => importConfig(event.target.files?.[0])}
            />
            <button className="button full" onClick={exportCsv}>
              <Download size={15} />
              Exportar resultado em CSV
            </button>
            <p className="fine-print">
              Não é necessário criar conta. Seus arquivos ficam no destino de
              download escolhido no navegador. A base pública é somente leitura.
            </p>
            <p className="fine-print">
              Os valores exibidos correspondem à última execução enviada. Edite
              e clique em Executar para atualizar.
            </p>
          </Card>
        </div>
      </div>
    </>
  );
}
