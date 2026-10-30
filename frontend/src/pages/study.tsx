import { useQuery } from "@tanstack/react-query";
import {
  ArrowDownToLine,
  ArrowUpRight,
  BookOpen,
  Database,
  Files,
} from "lucide-react";
import { api, assetUrl } from "../services/api";
import { Card, Loading, Notice } from "../components/ui";

type StudyFile = {
  name: string;
  title: string;
  description: string;
  url: string;
  bytes: number;
  sha256: string;
};
export function Study() {
  const query = useQuery({
    queryKey: ["study-files"],
    queryFn: () => api<StudyFile[]>("/files"),
    staleTime: Infinity,
  });
  if (query.isPending) return <Loading />;
  if (query.isError) return <Notice error>{query.error.message}</Notice>;
  return (
    <>
      <Notice>
        Acervo público do estudo. Você pode baixar os arquivos e reproduzir a
        análise sem conta, credenciais ou banco na nuvem. Os dados econômicos
        são hipóteses de um jogo fictício.
      </Notice>
      <div className="three-grid archive-grid">
        {query.data.map((file) => (
          <Card key={file.name} title={file.title}>
            <div className="archive-icon" aria-hidden="true">
              {file.name.endsWith(".pdf") ? (
                <BookOpen size={24} />
              ) : file.name.endsWith(".sqlite3") ? (
                <Database size={24} />
              ) : (
                <Files size={24} />
              )}
            </div>
            <p className="body-copy">{file.description}</p>
            <p className="fine-print">
              {file.name} ·{" "}
              {new Intl.NumberFormat("pt-BR", {
                maximumFractionDigits: 1,
              }).format(file.bytes / 1024)}{" "}
              KB
            </p>
            <a
              className={`button ${file.name.endsWith(".pdf") ? "primary" : ""}`}
              href={assetUrl(file.url)}
              {...(file.name.endsWith(".pdf")
                ? { target: "_blank", rel: "noreferrer" }
                : { download: file.name })}
            >
              {file.name.endsWith(".pdf")
                ? "Abrir PDF original"
                : "Baixar arquivo"}
              {file.name.endsWith(".pdf") ? (
                <ArrowUpRight size={15} />
              ) : (
                <ArrowDownToLine size={15} />
              )}
            </a>
            <details className="file-checksum">
              <summary>Verificar integridade do arquivo</summary>
              <code>SHA-256: {file.sha256}</code>
            </details>
          </Card>
        ))}
      </div>
      <div className="two-grid">
        <Card
          title="Consultar a base SQLite"
          subtitle="Uma edição fixa e reproduzível dos resultados oficiais"
        >
          <p className="body-copy">
            O banco inclui o catálogo, as estratégias, os quatro cenários, as
            premissas, 144 resultados mensais, 144 coortes, 40 resultados por
            produto e 14 referências de mercado. A aplicação o consulta somente
            para leitura.
          </p>
          <p className="body-copy">
            Depois de baixar o arquivo, você pode usar um visualizador SQLite ou
            o módulo sqlite3 do Python. Exemplo de consulta:
          </p>
          <pre className="sql-example">
            {
              "SELECT strategy, scenario, gross, flow\nFROM financial_comparison\nORDER BY flow DESC;"
            }
          </pre>
        </Card>
        <Card
          title="Explorar outras hipóteses"
          subtitle="A referência oficial permanece preservada"
        >
          <p className="body-copy">
            O simulador executa alterações no motor Python sem gravar no banco
            público. Exporte o CSV, o relatório PDF ou o arquivo JSON de
            hipóteses para guardar sua análise. O JSON pode ser importado
            novamente no simulador.
          </p>
          <p className="body-copy">
            As cópias originais em CSV mantêm a precisão do modelo fornecido. O
            CSV de comparação usa o mesmo arredondamento monetário exibido pela
            aplicação.
          </p>
        </Card>
      </div>
    </>
  );
}
