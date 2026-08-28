"""실행 중인 웹서비스에서 발표자료용 화면 이미지를 캡처한다."""

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "ppt" / "assets"


async def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1.5)
        await page.goto("http://127.0.0.1:8765", wait_until="networkidle")

        prediction = page.locator("#prediction")
        await prediction.locator('input[name="speed_kmh"]').fill("70")
        await prediction.locator('input[name="payload_kg"]').fill("180")
        await prediction.locator('input[name="trip_distance_km"]').fill("50")
        await page.locator('button[form="prediction-form"]').click()
        await page.locator("#prediction-result").wait_for(state="visible")
        await prediction.screenshot(path=ASSET_DIR / "web_prediction.png")

        await page.locator('[data-tab="simulation"]').click()
        simulation = page.locator("#simulation")
        await simulation.locator('#current-form input[name="speed_kmh"]').fill("150")
        await simulation.locator('#current-form input[name="payload_kg"]').fill("600")
        await simulation.locator('#current-form input[name="trip_distance_km"]').fill("250")
        await simulation.locator('button[type="submit"]').click()
        await page.locator("#simulation-result").wait_for(state="visible")
        await simulation.screenshot(path=ASSET_DIR / "web_simulation_warning.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
