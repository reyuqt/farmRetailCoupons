const fetch = require("node-fetch");
const commandLineArgs = require("command-line-args");

// Command-line options definition
const optionDefinitions = [
    { name: "couponType", alias: "c", type: String, defaultValue: "TEN_OFF" },
    { name: "serverPort", alias: "s", type: Number, defaultValue: 8000 },
    { name: "host", type: String },
    { name: "port", type: String },
    { name: "username", type: String },
    { name: "password", type: String },
    { name: "protocol", type: String },
];
const options = commandLineArgs(optionDefinitions);

/**
 * Selects a random element from an array.
 * @param {Array} arr - The array to sample from.
 * @returns {*} A random element from the array.
 */
function sample(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

/**
 * Makes a GET request to the specified path.
 * @param {string} path - The API endpoint path.
 * @returns {Promise<Response>} The fetch response.
 */
async function makeRequest(path) {
    const url = `http://127.0.0.1:${options.serverPort}/${path}`;
    console.log(`Sending GET request to: ${url}`);
    return fetch(url);
}

/**
 * Makes a POST request to the specified path with data.
 * @param {string} path - The API endpoint path.
 * @param {Object} data - The data to send in the request body.
 * @returns {Promise<Response>} The fetch response.
 */
async function postRequest(path, data) {
    const url = `http://127.0.0.1:${options.serverPort}/${path}`;
    console.log(`Sending POST request to: ${url}`);
    return fetch(url, {
        method: "POST",
        headers: {
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
}

/**
 * Generates a random number between min and max (inclusive).
 * @param {number} min - The minimum value.
 * @param {number} max - The maximum value.
 * @returns {number} A random integer between min and max.
 */
const randomNumber = (min, max) => Math.floor(Math.random() * (max - min + 1) + min);

/**
 * Sleeps for a random duration around the specified millis.
 * @param {number} millis - The base duration in milliseconds.
 * @returns {Promise<void>} Resolves after the sleep duration.
 */
const sleep = (millis) => {
    const adjustedMillis = randomNumber(millis - 200, millis + 200);
    return new Promise((resolve) => setTimeout(resolve, adjustedMillis));
};

/**
 * Captures a screenshot of the current page.
 * @param {import('puppeteer').Page} page - Puppeteer page instance.
 * @param {string} [name] - Optional name for the screenshot file.
 */
async function ErrorScreenshot(page, name = "") {
    const timestamp = Date.now();
    const fileName = `${timestamp}${name ? `_${name}` : ""}.jpg`;
    console.log(`Saving screenshot as: ${fileName}`);
    await page.screenshot({ path: `./${fileName}` });
}


// Module exports
module.exports = {
    sample,
    makeRequest,
    postRequest,
    randomNumber,
    sleep,
    options,
    ErrorScreenshot,
};
