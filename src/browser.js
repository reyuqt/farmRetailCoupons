const puppeteer = require('puppeteer-extra');
const proxyChain = require('proxy-chain');
const { options } = require('./utils');
const AdblockerPlugin = require('puppeteer-extra-plugin-adblocker');

// Use plugins with Puppeteer
puppeteer.use(require('puppeteer-extra-plugin-stealth')());
puppeteer.use(require('puppeteer-extra-plugin-repl')());
puppeteer.use(AdblockerPlugin({ blockTrackers: true }));

/**
 * Creates a Puppeteer browser instance with the appropriate settings.
 *
 * @returns {Promise<import('puppeteer').Browser>} The configured Puppeteer browser instance.
 */
async function makeBrowser() {
    try {
        // Base arguments for Puppeteer
        const args = [
            '--disable-infobars',
            '--window-size=1600,1200',
            '--no-sandbox',
        ];

        // Configure proxy settings if provided
        if (options.host) {
            let proxyString = `${options.protocol}://${options.host}:${options.port}`;

            // Use proxy authentication if credentials are provided
            if (options.username) {
                proxyString = await proxyChain.anonymizeProxy(
                    `${options.protocol}://${options.username}:${options.password}@${options.host}:${options.port}`
                );
            }

            args.push(`--proxy-server=${proxyString}`);
            args.push(`--host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE ${options.host}"`);
            args.push(`--disable-extensions-except=${__dirname}/extensions/webrtc`);
            args.push(`--load-extension=${__dirname}/extensions/webrtc`);
        }

        // Launch the Puppeteer browser
        return await puppeteer.launch({
            headless: false,
            defaultViewport: null,
            args,
        });
    } catch (error) {
        console.error('Error launching browser:', error);
        throw error;
    }
}

module.exports = { makeBrowser };
