import { describe, it, expect, afterEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { DataTable, Metric, brl } from "./ui";
afterEach(cleanup);
describe("Dados e interpretação", () => {
  it("formata reais e explica um indicador", () => {
    render(
      <Metric
        label="CAC"
        value={brl(10)}
        note="Por adquirido"
        help="Marketing dividido por adquiridos"
      />,
    );
    expect(screen.getByText(/10,00/)).toBeInTheDocument();
    fireEvent.click(screen.getByLabelText("Explicação: CAC"));
    expect(screen.getByText("Marketing dividido por adquiridos")).toBeVisible();
  });
  it("filtra, ordena e pagina registros", () => {
    render(
      <DataTable
        rows={Array.from({ length: 12 }, (_, i) => ({
          name: `Coorte ${i + 1}`,
          value: 12 - i,
        }))}
        columns={[
          { key: "name", label: "Coorte" },
          { key: "value", label: "Valor" },
        ]}
        searchable
      />,
    );
    expect(screen.getByText("Coorte 1")).toBeInTheDocument();
    expect(screen.queryByText("Coorte 12")).not.toBeInTheDocument();
    fireEvent.click(screen.getByLabelText("Próxima página"));
    expect(screen.getByText("Coorte 12")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Filtrar tabela"), {
      target: { value: "Coorte 12" },
    });
    expect(screen.queryByText("Coorte 1")).not.toBeInTheDocument();
    expect(screen.getByText("Coorte 12")).toBeInTheDocument();
  });
});
