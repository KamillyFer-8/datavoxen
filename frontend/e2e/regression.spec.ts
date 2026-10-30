import { test, expect } from "@playwright/test";
// Regressões dos fluxos públicos do estudo.
test("navega pelos módulos com dados da API e sem erro de execução", async ({
  page,
}, testInfo) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.getByText(/1\.160\.759,47/)).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Evolução da receita" }),
  ).toBeVisible();
  await page.waitForFunction(
    () => document.documentElement.scrollHeight > 1000,
  );
  await page.screenshot({
    path: `../output/prints/${testInfo.project.name}/dashboard-regression.png`,
    fullPage: true,
    animations: "disabled",
    scale: "css",
  });
  for (const [route, title] of [
    ["estrategias", "Estratégias comerciais"],
    ["produtos", "Produtos e precificação"],
    ["jogadores", "Jogadores e coortes"],
    ["financas", "Finanças e viabilidade"],
    ["benchmarking", "Benchmarking de mercado"],
    ["relatorios", "Relatórios e exportação"],
    ["metodologia", "Metodologia e fontes"],
    ["estudo", "Arquivos do estudo"],
  ]) {
    await page.goto("/" + route);
    await expect(
      page.getByRole("heading", { name: title, exact: true }),
    ).toBeVisible();
    await expect(
      page
        .getByRole("status")
        .filter({ hasText: "Consultando o motor financeiro" }),
    ).toHaveCount(0);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBeTruthy();
  }
  expect(errors).toEqual([]);
});
test("valida parâmetros e abre a navegação móvel", async ({
  page,
}, testInfo) => {
  await page.goto("/simulador");
  await page.getByLabel("CAC por adquirido").fill("-1");
  await page.getByRole("button", { name: "Executar simulação" }).click();
  await expect(page.getByRole("alert")).toContainText("Confira os valores");
  await page.getByLabel("CAC por adquirido").fill("12");
  await page.getByRole("button", { name: "Executar simulação" }).click();
  await expect(page.getByText(/1\.304\.759,47/)).toBeVisible();
  await page.screenshot({
    path: `../output/prints/${testInfo.project.name}/simulador-regression.png`,
    fullPage: true,
  });
  if (testInfo.project.name === "mobile") {
    await page.getByRole("button", { name: "Abrir navegação" }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByRole("button", { name: "Abrir navegação" })).toBeFocused();
    await page.getByRole("button", { name: "Abrir navegação" }).click();
    await page.getByRole("link", { name: "Finanças", exact: true }).click();
    await expect(
      page.getByRole("heading", {
        name: "Finanças e viabilidade",
        exact: true,
      }),
    ).toBeVisible();
  }
});
test('restaura os parâmetros ao alternar referências já consultadas', async ({page})=>{
  await page.goto('/simulador');
  await expect(page.getByLabel('CAC por adquirido')).toHaveValue('10');
  await page.getByLabel('CAC por adquirido').fill('12');
  await page.getByRole('button',{name:'Executar simulação'}).click();
  await expect(page.getByText(/1\.304\.759,47/)).toBeVisible();
  await page.getByLabel('Estratégia',{exact:true}).selectOption('B');
  await expect(page.getByLabel('CAC por adquirido')).toHaveValue('10');
  await page.getByLabel('Estratégia',{exact:true}).selectOption('A');
  await expect(page.getByLabel('CAC por adquirido')).toHaveValue('10');
  await expect(page.locator('.large-stat')).toContainText('1.160.759,47');
});
test("simula CAC e exporta valores atualizados", async ({ page }) => {
  await page.goto("/simulador");
  await page.getByLabel("CAC por adquirido").fill("12");
  await page.getByRole("button", { name: "Executar simulação" }).click();
  await expect(page.getByText(/1\.304\.759,47/)).toBeVisible();
  await page.goto("/");
  await page.getByLabel("Estratégia", { exact: true }).selectOption("C");
  await expect(page.getByText(/1\.211\.175,43/)).toBeVisible();
  await page.goto("/relatorios");
  const exported = page.waitForEvent("download");
  await page.getByRole("button", { name: "Baixar CSV" }).first().click();
  expect((await exported).suggestedFilename()).toContain(".csv");
});
