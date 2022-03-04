import React from 'react';
import sinon from 'sinon';
import * as Hooks from '~/hooks';
import { useNextEntity, usePreviousEntity, useSelectedEntity } from './hooks';

beforeAll(() => {
  sinon.stub(React, 'useContext');
  sinon.stub(Hooks, 'useAppSelector').callsFake((cb) =>
    cb({
      entities: {
        entities: [
          { pk: 1, original: 'hello' },
          { pk: 2, original: 'world' },
          { pk: 3 },
        ],
      },
    }),
  );
});
afterAll(() => {
  React.useContext.restore();
  Hooks.useAppSelector.restore();
});

describe('hooks', () => {
  describe('useNextEntity', () => {
    it('returns the next entity in the list', () => {
      React.useContext.returns({ entity: 1 });
      expect(useNextEntity()).toMatchObject({ pk: 2 });
    });

    it('returns the first entity when the last one is selected', () => {
      React.useContext.returns({ entity: 3 });
      expect(useNextEntity()).toMatchObject({ pk: 1 });
    });

    it('returns undefined when the current entity does not exist', () => {
      React.useContext.returns({ entity: 5 });
      expect(useNextEntity()).toBeUndefined();
    });
  });

  describe('usePreviousEntity', () => {
    it('returns the previous entity in the list', () => {
      React.useContext.returns({ entity: 2 });
      expect(usePreviousEntity()).toMatchObject({ pk: 1 });
    });

    it('returns the last entity when the first one is selected', () => {
      React.useContext.returns({ entity: 1 });
      expect(usePreviousEntity()).toMatchObject({ pk: 3 });
    });

    it('returns undefined when the current entity does not exist', () => {
      React.useContext.returns({ entity: 5 });
      expect(usePreviousEntity()).toBeUndefined();
    });
  });

  describe('useSelectedEntity', () => {
    it('returns the selected entity', () => {
      React.useContext.returns({ entity: 2 });
      expect(useSelectedEntity()).toMatchObject({ pk: 2, original: 'world' });
    });

    it('returns undefined if the entity is missing', () => {
      React.useContext.returns({ entity: 5 });
      expect(useSelectedEntity()).toBeUndefined();
    });
  });
});
