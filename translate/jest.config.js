/* eslint-env commonjs */
/* global module */
const { ignoreFromJest } = require('./test-ownership');

/** @type {import('@jest/types').Config.InitialOptions} */
module.exports = {
  verbose: true,
  roots: ['<rootDir>/src'],
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  collectCoverage: true,
  collectCoverageFrom: ['src/**/*.{js,jsx,ts,tsx}', '!src/**/*.d.ts'],
  coveragePathIgnorePatterns: ['<rootDir>/node_modules/'],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
  ],
  testEnvironment: './jest-jsdom-fix.mjs',
  preset: 'ts-jest',
  testPathIgnorePatterns: ignoreFromJest,
  transform: {
    '\\.jsx?$': ['babel-jest', { configFile: '../babel.config.json' }],
    '\\.tsx?$': 'ts-jest',
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(@fluent|@mozilla|messageformat)/).+\\.(c?js)$',
  ],
  resetMocks: true,
  moduleNameMapper: {
    '.+\\.(css|styl|less|sass|scss|png|jpg|ttf|woff|woff2)$':
      'identity-obj-proxy',
    '\\.svg$': '<rootDir>/__mocks__/svg.js',
    '~(.*)$': '<rootDir>/src/$1',
  },
  testTimeout: 10000, // optional
};
