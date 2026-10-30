import { test, expect } from "@playwright/test";
import { readFile } from "node:fs/promises";

test("acervo público permite baixar SQLite e abrir o PDF original", async ({
  page,
}) => {
  await page.goto("/estudo");
  await expect(
    page.getByRole("heading", { name: "Arquivos do estudo", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Base SQLite do estudo", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("link", { name: "Abrir PDF original", exact: true }),
  ).toHaveAttribute("href", /\/api\/files\/estudo-original.pdf$/);
  const download = page.waitForEvent("download");
  await page.locator('a[href$="/datavoxen.sqlite3"]').click();
  const file = await download;
  expect(file.suggestedFilename()).toBe("datavoxen.sqlite3");
  const path = await file.path();
  expect(path).toBeTruthy();
  expect((await readFile(path!)).subarray(0, 16).toString()).toBe(
    "SQLite format 3\u0000",
  );
  await page.goto("/conta");
  await expect(page).toHaveURL(/\/estudo$/);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
});

test("guarda hipóteses em JSON e recupera sem conta", async ({
  page,
}, testInfo) => {
  await page.goto("/simulador");
  await page.getByLabel("CAC por adquirido").fill("12");
  await page.getByRole("button", { name: "Executar simulação" }).click();
  await expect(page.getByText(/1\.304\.759,47/)).toBeVisible();
  const downloaded = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Baixar hipóteses (JSON)", exact: true })
    .click();
  const config = await downloaded;
  const filePath = testInfo.outputPath("hipoteses.json");
  await config.saveAs(filePath);
  expect(JSON.parse(await readFile(filePath, "utf-8")).overrides.cac).toBe(12);
  await page.getByRole("button", { name: "Restaurar referência" }).click();
  await expect(page.getByText(/1\.160\.759,47/).first()).toBeVisible();
  await page.getByLabel("Arquivo de hipóteses").setInputFiles(filePath);
  await expect(page.getByText(/1\.304\.759,47/)).toBeVisible();
  await page
    .getByLabel("Arquivo de hipóteses")
    .setInputFiles({
      name: "invalido.json",
      mimeType: "application/json",
      buffer: Buffer.from('{"model_version":"outra"}'),
    });
  await expect(
    page.getByText("O arquivo pertence a outra versão do modelo."),
  ).toBeVisible();
});
