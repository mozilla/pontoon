import React from 'react';
import sinon from 'sinon';
import * as Hooks from '~/hooks';
import { useLocation } from './useLocation';

beforeAll(() => {
  sinon.stub(Hooks, 'useAppSelector');
  sinon.stub(React, 'useMemo').callsFake((cb) => cb());
});
afterAll(() => {
  Hooks.useAppSelector.restore();
  React.useMemo.restore();
});

const fakeSelector = (pathname, search) => (sel) =>
  sel({ router: { location: { pathname, search } } });

describe('useLocation', () => {
  it('correctly parses the pathname', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector('/kg/waterwolf/path/to/RESOURCE.po/', ''),
    );

    expect(useLocation()).toMatchObject({
      locale: 'kg',
      project: 'waterwolf',
      resource: 'path/to/RESOURCE.po',
      entity: 0,
    });
  });

  it('correctly parses the query string', () => {
    Hooks.useAppSelector.callsFake(
      fakeSelector('/kg/waterwolf/path/', '?string=42'),
    );

    expect(useLocation()).toMatchObject({
      locale: 'kg',
      project: 'waterwolf',
      resource: 'path',
      entity: 42,
    });
  });
});
