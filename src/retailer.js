const { makeRequest, postRequest, sample, sleep, options } = require("./utils");
const RETAILER_URL = 'website.com'
/**
 * Open a category on the shopping page.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 */
async function openCategory(page) {
    try {
        const button = await page.$('button[data-linkid="shop"]');
        await button.scrollIntoView();
        await Promise.all([
            page.waitForNavigation(),
            searchCategory(page),
            page.waitForResponse((r) => r.url().includes(`${RETAILER_URL}/pl/`)),
        ]);
        await addItem(page);
    } catch (error) {
        console.error("Error in openCategory:", error);
        throw new Error("Failed to open category");
    }
}

/**
 * Search and navigate through categories.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 */
async function searchCategory(page) {
    await makeRequest("shop");
    await saveCookies(page);

    const level1Cats = await page.$$('#flyout-content li[id^="flyout_Section_"]');
    const level1Cat = await sample(level1Cats);
    await level1Cat.hover();
    await sleep(2000);

    const level2Cats = await page.$$('#flyout-content li[id^="l2_flyout_Section_"]');
    const level2Cat = await sample(level2Cats);
    await level2Cat.hover();
    await sleep(2000);

    const level3Cats = await page.$$('#flyout-content li[id^="l3_flyout_Section_"]');
    if (level3Cats.length === 0) {
        await level2Cat.click();
    } else {
        const level3Cat = await sample(level3Cats);
        await level3Cat.click();
    }
}

/**
 * Open the promo code input box.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 * @param {number} [attempts=1] - Number of attempts made to open the box
 */
async function openPromoBox(page, attempts = 1) {
    try {
        if (await page.$('.accordion-addPromoCode-header-collapsed div')) {
            await Promise.all([
                makeRequest("open_promo_code"),
                sleep(5000),
            ]);
        }
    } catch (error) {
        console.warn(`Retrying openPromoBox (Attempt ${attempts}):`, error);
        if (attempts < 3) await openPromoBox(page, attempts + 1);
        else throw new Error("Failed to open promo box after 3 attempts");
    }
}

/**
 * Navigate to the shopping cart.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 */
async function goToCart(page) {
    try {
        const cartButton = await page.$("#cart-preview-wrapper a");
        await Promise.all([
            page.waitForResponse((r) => r.url().includes(`${RETAILER_URL}/cart`)),
            cartButton.click(),
        ]);
    } catch (error) {
        console.error("Error in goToCart:", error);
        throw new Error("Failed to navigate to cart");
    }
}

/**
 * Save cookies to the database.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 */
async function saveCookies(page) {
    const cookies = await page.cookies();
    await postRequest("save_cookies", { value: cookies });
}

/**
 * Add an item to the cart.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 */
async function addItem(page) {
    try {
        await sleep(5000);
        const buttons = await page.$$('button[id*="add-to-cart"]');
        const button = sample(buttons);
        const button2 = sample(buttons);

        await button2.click();
        await sleep(5000);
        await button.scrollIntoView();
        await sleep(5000);

        await Promise.all([
            page.waitForResponse(`https://${RETAILER_URL}/purchase/api/cart/cartitems`),
            makeRequest("add_to_cart"),
        ]);

        const closeButton = await page.$(".header-close-bt");
        await closeButton.click();
        await saveCookies(page);
    } catch (error) {
        console.error("Error in addItem:", error);
        throw new Error("Failed to add item");
    }
}

/**
 * Remove the promo code from the cart.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 */
async function removePromoCode(page) {
    try {
        const removeButton = await page.$('*[data-automation-id="remove-promo-code"]');
        if (removeButton) {
            await Promise.all([
                sleep(5000),
                removeButton.click(),
            ]);
            console.info("Promo code removed");
        } else {
            console.info("No promo code to remove");
        }
    } catch (error) {
        console.error("Error in removePromoCode:", error);
    }
}

/**
 * Add a promo code to the cart.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 * @returns {Promise<object>} The response data for the promo code addition
 */
async function addPromoCode(page) {
    try {
        const [promoResponse] = await Promise.all([
            page.waitForResponse((r) => /purchase\/api\/cart\/\d+\/promocode/.test(r.url())),
            makeRequest(`input_promo_code/${options.couponType}`),
        ]);
        return await promoResponse.json();
    } catch (error) {
        console.error("Error in addPromoCode:", error);
        throw new Error("Failed to add promo code");
    }
}

/**
 * Check the status of the promo code.
 * @param {object} response - The promo code API response
 */
async function checkPromoCode(response) {
    try {
        if (response.data?.coupons[0]?.isValid && response.data?.coupons.length === 1) {
            await makeRequest(`valid_coupon/${options.couponType}/${response.data.coupons[0].couponCode}`);
        } else if (response.data?.coupons.length > 1 && response.data?.coupons[1]?.isValid) {
            await makeRequest(`valid_coupon/${options.couponType}/${response.data.coupons[1].couponCode}`);
        } else if (response.data?.coupons[0]?.isValid === false) {
            await makeRequest(`invalid_coupon/${options.couponType}/${response.data.coupons[0].couponCode}`);
        } else {
            console.warn("Unexpected promo code response:", JSON.stringify(response.data, null, 2));
        }
        await sleep(4000);
    } catch (error) {
        console.error("Error in checkPromoCode:", error);
    }
}

/**
 * Check for promo code error messages.
 * @param {import('puppeteer').Page} page - Puppeteer page instance
 * @returns {Promise<boolean>} Whether an error message was found
 */
async function checkPromoError(page) {
    try {
        const element = await page.$('[data-automation-id="promo-code-container"]');
        const textContent = await element.evaluate((el) => el.textContent);
        return /attempts/.test(textContent);
    } catch (error) {
        console.error("Error in checkPromoError:", error);
        return false;
    }
}

// Export functions
module.exports = {
    openCategory,
    addItem,
    openPromoBox,
    addPromoCode,
    checkPromoCode,
    removePromoCode,
    goToCart,
    checkPromoError,
    RETAILER_URL
};
