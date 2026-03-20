import { chromium } from "playwright";
import path from "path";

const states = [
  //   "Andaman and Nicobar",
  //   "Andhra Pradesh",
  //   "Arunachal Pradesh",
  //   "Assam",
  //   "Bihar",
  "Chandigarh",
  //   "Chhattisgarh",
  "Delhi",
  //   "Gujarat",
  //   "Haryana",
  //   "Himachal Pradesh",
  //   "Jammu and Kashmir",
  //   "Jharkhand",
  //   "Karnataka",
  //   "Kerala",
  //   "Madhya Pradesh",
  "Maharashtra",
  //   "Manipur",
  //   "Meghalaya",
  //   "Mizoram",
  //   "Nagaland",
  //   "Odisha",
  "Puducherry",
  //   "Punjab",
  //   "Rajasthan",
  //   "Sikkim",
  //   "Tamil Nadu",
  //   "Telangana",
  //   "Tripura",
  "Uttar Pradesh",
  //   "Uttarakhand",
  //   "West Bengal",
];

const url =
  "https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-data-repository";

async function visitWebsite() {
  const browser = await chromium.launch({ headless: false, slowMo: 400 });
  const page = await browser.newPage();
  await page.goto(url);

  await page.getByText("▼").first().click();
  await page.getByText("Raw data").click();
  await page.getByText("▼").nth(1).click();
  await page.getByText("1 hour").click();

  // state dropdown
  await page.getByText("▼").nth(2).click();
  await page.locator(".options li").first().waitFor();
  //   const states = await page
  //     .locator(".options li")
  //     .evaluateAll((elements) => elements.map((el) => el.textContent.trim()));
  //await page.getByText(states[1]).click();

  for (const [i, state] of states.entries()) {
    if (i > 0) await page.getByText("▼").nth(2).click();
    await page.getByText(state).click();

    // city dropdown
    await page.getByText("▼").nth(3).click();
    await page.locator(".options li").first().waitFor();
    const cities = await page
      .locator(".options li")
      .evaluateAll((elements) => elements.map((el) => el.textContent.trim()));

    for (const [j, city] of cities.entries()) {
      if (j > 0) await page.getByText("▼").nth(3).click();
      await page.getByText(city).click();

      // station dropdown
      await page.getByText("▼").nth(4).click();
      await page.locator(".options li").first().waitFor();
      const stations = await page
        .locator(".options li")
        .evaluateAll((elements) => elements.map((el) => el.textContent.trim()));

      for (const [k, station] of stations.entries()) {
        if (k > 0) await page.getByText("▼").nth(4).click();
        await page.getByText(station).click();

        await page.getByRole("button", { name: "Submit" }).click();

        for (const year of ["2020", "2021", "2022", "2023", "2024", "2025"]) {
          const rowLocator = page.getByRole("row", { name: year }).locator("a");
          if (!(await rowLocator.isVisible())) continue;

          const popupPromise = page.waitForEvent("popup");
          const downloadPromise = page.waitForEvent("download");

          await page.getByRole("row", { name: year }).locator("a").click();

          await popupPromise;
          const download = await downloadPromise;

          console.log(
            `Downloading data for ${state} - ${city} - ${station} - ${year}`,
          );

          const downloadPath =
            "data/" + state + "/" + city + "/" + station + "/" + year + ".csv";
          await download.saveAs(path.join(downloadPath));
          await download.saveAs(
            path.join("combined/", await download.suggestedFilename()),
          );
          await download.delete();
        }
      }
    }
  }
  console.log("All downloads completed!");
  await browser.close();
}

visitWebsite();
