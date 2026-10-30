import { test, expect } from "@playwright/test";

test("captura todas as telas para entrega", async ({ page }, testInfo) => {
  test.setTimeout(180000);
  const screens = [
    ["01-visao-geral", "/", "Visão geral"],
    ["02-estrategias", "/estrategias", "Estratégias comerciais"],
    ["03-simulador", "/simulador", "Simulador financeiro"],
    ["04-produtos", "/produtos", "Produtos e precificação"],
    ["05-jogadores-coortes", "/jogadores", "Jogadores e coortes"],
    ["06-financas", "/financas", "Finanças e viabilidade"],
    ["07-benchmarking", "/benchmarking", "Benchmarking de mercado"],
    ["08-relatorios", "/relatorios", "Relatórios e exportação"],
    ["09-metodologia", "/metodologia", "Metodologia e fontes"],
    ["10-estudo", "/estudo", "Arquivos do estudo"],
  ];
  for (const [name, path, title] of screens) {
    await page.goto(path);
    await expect(
      page.getByRole("heading", { name: title, exact: true }),
    ).toBeVisible();
    await expect(page.locator(".card").first()).toBeVisible();
    await expect(page.locator(".loading")).toHaveCount(0);
    if (path === "/simulador") {
      const collapsed = page.locator(
        ".parameter-section:not([open]) > summary",
      );
      while (await collapsed.count()) await collapsed.first().click();
    }
    if (path === "/produtos")
      await expect(
        page.locator(".compact-metrics .metric > strong").first(),
      ).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    await page
      .getByRole("heading", { name: title, exact: true })
      .scrollIntoViewIfNeeded();
    await page.screenshot({
      path: `../output/prints/${testInfo.project.name}/${name}.png`,
      fullPage: true,
      animations: "disabled",
      scale: "css",
    });
  }
  if (testInfo.project.name === "mobile") {
    await page.getByRole("button", { name: "Abrir navegação" }).click();
    await expect(
      page.getByRole("link", { name: "Visão geral", exact: true }),
    ).toBeVisible();
    await page.screenshot({
      path: "../output/prints/mobile/11-menu.png",
      animations: "disabled",
      scale: "css",
    });
  }
});
