/* eslint-env node */

module.exports = {
    testURL: 'https://nowhere.com/at/all',
    moduleNameMapper: {
        '\\.(css|less)$': 'identity-obj-proxy',
    },
    setupFiles: ['./src/setupTests.js'],
    collectCoverage: true,
};
