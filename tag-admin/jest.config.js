/* eslint-env node */

/** @type {import('@jest/types').Config.InitialOptions} */
module.exports = {
  testEnvironment: 'jsdom',
  testEnvironmentOptions: { url: 'https://nowhere.com/at/all' },
  moduleNameMapper: {
    '\\.(css|less)$': 'identity-obj-proxy',
  },
  setupFiles: ['./src/setupTests.js'],
  transform: {
    '\\.[jt]sx?$': ['babel-jest', { configFile: '../babel.config.json' }],
  },
  collectCoverage: true,
};
