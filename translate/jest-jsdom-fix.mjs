import { TestEnvironment } from 'jest-environment-jsdom';

// Hacky fix for https://github.com/jsdom/jsdom/issues/3363
export default class FixedEnvironment extends TestEnvironment {
  constructor(...args) {
    super(...args);
    this.global.structuredClone = structuredClone;
  }
}
