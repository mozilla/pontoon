/* eslint-env node */

/** @type {import('@jest/types').Config.InitialOptions} */
module.exports = {
    testEnvironment: 'jsdom',
    testURL: 'https://nowhere.com/at/all',
    moduleNameMapper: {
        '\\.(css|less)$': 'identity-obj-proxy',
    },
    setupFiles: ['./src/setupTests.js'],
    collectCoverage: true,
};
