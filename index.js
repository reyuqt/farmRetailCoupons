const { sleep, ErrorScreenshot } = require("./src/utils");
const {
    openCategory,
    goToCart,
    openPromoBox,
    addPromoCode,
    removePromoCode,
    checkPromoCode,
    checkPromoError,
    RETAILER_URL,
} = require("./src/retailer");
const { makeBrowser } = require("./src/browser");

/**
 * Tests a coupon by navigating through the necessary steps.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 */
async function testCoupon(page) {
    try {
        await goToCart(page);
        await sleep(5000);
        await openPromoBox(page);
        const response = await addPromoCode(page);
        await checkPromoCode(response);
        await removePromoCode(page);
    } catch (error) {
        console.error("Error in testCoupon:", error);
        await ErrorScreenshot(page, "testCoupon");

        try {
            const response = await checkPromoError(page);
            console.log(`Response from checkPromoError: ${response}`);
        } catch (nestedError) {
            console.error("Error during checkPromoError:", nestedError);
        }

        throw error; // Re-throw the error to handle it in the calling function
    }
}

/**
 * Retries a function up to a specified number of times.
 * @param {Function} fn - The function to retry
 * @param {number} retries - Number of retries
 */
async function retry(fn, retries = 3) {
    let lastError;

    for (let attempt = 1; attempt <= retries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            console.warn(`Attempt ${attempt} failed. Retrying...`);
        }
    }

    throw lastError; // Throw the last error if all retries fail
}

(async () => {
    const browser = await makeBrowser();

    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1600, height: 1200 });
        await page.goto(`https://${RETAILER_URL}/cart`);

        // Open category with retries
        await retry(() => openCategory(page), 3);

        await sleep(5000);

        // Test coupon with retries
        await retry(async () => {
            await testCoupon(page);
            await testCoupon(page); // Perform additional coupon tests as needed
        }, 5);
    } catch (error) {
        console.error("Critical error:", error);
    } finally {
        await browser.close();
        process.exit(0);
    }
})();
