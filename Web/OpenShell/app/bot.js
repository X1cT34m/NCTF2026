const express = require("express");
const { chromium } = require("playwright-core");

const app = express();
app.use(express.json());

const visitUrl = async (url) => {
    let browser;
    try {
        browser = await chromium.launch({
            headless: true,
            executablePath: "/usr/bin/chromium-headless-shell",
            args: [
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
            ],
        });
        const context = await browser.newContext();
        const page = await context.newPage();
        await page.goto(url, { waitUntil: "domcontentloaded", timeout: 15_000 });
        await page.waitForTimeout(15_000);
        await context.close();
    } catch (error) {
        console.error(JSON.stringify({ url, error: String(error) }));
    } finally {
        if (browser) {
            await browser.close();
        }
    }
};

app.post("/report", (req, res) => {
    const { url } = req.body;
    const parsed = new URL(url);

    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
        return res.status(400).json({
            ok: false,
            error: "invalid url",
        });
    }

    if (!parsed.hostname.endsWith('.pages.dev')) {
        return res.status(400).json({
            ok: false,
            error: "invalid url",
        });
    }

    setImmediate(() => visitUrl(url));

    return res.status(200).json({
        ok: true,
        message: "accepted",
    });
});

app.listen(8000, "0.0.0.0", () => {
    console.log(`bot listening on 0.0.0.0:8000`);
});
