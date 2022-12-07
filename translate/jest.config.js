/* eslint-env commonjs */

/** @type {import('@jest/types').Config.InitialOptions} */
module.exports = {
  verbose: true,
  roots: ['<rootDir>/src'],
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  collectCoverageFrom: ['src/**/*.{js,jsx,ts,tsx}', '!src/**/*.d.ts'],
  coveragePathIgnorePatterns: ['<rootDir>/node_modules/'],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
  ],
  testEnvironment: 'jsdom',
  preset: 'ts-jest',
  transform: {
    '\\.jsx?$': ['babel-jest', { configFile: '../babel.config.json' }],
    '\\.tsx?$': ['ts-jest', { isolatedModules: true }],
  },
  transformIgnorePatterns: [
    '[/\\\\]node_modules[/\\\\].+\\.(js|jsx|mjs|cjs|ts|tsx)$',
  ],
  resetMocks: true,
  moduleNameMapper: {
    '.+\\.(css|styl|less|sass|scss|png|jpg|ttf|woff|woff2)$':
      'identity-obj-proxy',
    '\\.svg$': '<rootDir>/__mocks__/svg.js',
    '~(.*)$': '<rootDir>/src/$1',
  },
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],
  testTimeout: 10000, // optional
};
