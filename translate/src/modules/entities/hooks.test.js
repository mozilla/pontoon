import React from 'react';
import sinon from 'sinon';

import * as Hooks from '~/hooks';
import { useNextEntity, usePreviousEntity } from './hooks';

const ENTITIES = [
  { pk: 1, original: 'hello' },
  { pk: 2, original: 'world' },
  { pk: 3 },
];

beforeAll(() => {
  sinon.stub(React, 'useContext');
  sinon
    .stub(Hooks, 'useAppSelector')
    .callsFake((cb) => cb({ entities: { entities: ENTITIES } }));
});
afterAll(() => {
  React.useContext.restore();
  Hooks.useAppSelector.restore();
});

describe('hooks', () => {
  describe('useNextEntity', () => {
    it('returns the next entity in the list', () => {
      React.useContext.returns({ entity: ENTITIES[0] });
      expect(useNextEntity()).toBe(ENTITIES[1]);
    });

    it('returns the first entity when the last one is selected', () => {
      React.useContext.returns({ entity: ENTITIES[2] });
      expect(useNextEntity()).toBe(ENTITIES[0]);
    });

    it('returns null when the current entity does not exist', () => {
      React.useContext.returns({ entity: { pk: 99 } });
      expect(useNextEntity()).toBeNull();
    });
  });

  describe('usePreviousEntity', () => {
    it('returns the previous entity in the list', () => {
      React.useContext.returns({ entity: ENTITIES[1] });
      expect(usePreviousEntity()).toBe(ENTITIES[0]);
    });

    it('returns the last entity when the first one is selected', () => {
      React.useContext.returns({ entity: ENTITIES[0] });
      expect(usePreviousEntity()).toBe(ENTITIES[2]);
    });

    it('returns null when the current entity does not exist', () => {
      React.useContext.returns({ entity: { pk: 99 } });
      expect(usePreviousEntity()).toBeNull();
    });
  });
});
