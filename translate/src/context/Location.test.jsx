import React, { useContext } from 'react';

import { LocationProvider, Location } from './Location';
import { render } from '@testing-library/react';
import { vi } from 'vitest';

describe('LocationProvider', () => {
  it('correctly parses the pathname', () => {
    let view;
    const Spy = () => {
      view = useContext(Location);
      return null;
    };

    const history = {
      location: { pathname: '/kg/waterwolf/path/to/RESOURCE.po/', search: '' },
      listen: vi.fn(),
    };

    render(
      <LocationProvider history={history}>
        <Spy />
      </LocationProvider>,
    );

    expect(view).toMatchObject({
      locale: 'kg',
      project: 'waterwolf',
      resource: 'path/to/RESOURCE.po',
      entity: 0,
      status: null,
    });
  });

  it('correctly parses a query string', () => {
    let view;
    const Spy = () => {
      view = useContext(Location);
      return null;
    };
    const history = {
      location: {
        pathname: '/kg/waterwolf/path/',
        search: '?status=missing,warnings&string=42',
      },
      listen: vi.fn(),
    };
    render(
      <LocationProvider history={history}>
        <Spy />
      </LocationProvider>,
    );

    expect(view).toMatchObject({
      locale: 'kg',
      project: 'waterwolf',
      resource: 'path',
      entity: 42,
      status: 'missing,warnings',
    });
  });

  it('correctly parses a query string with a list', () => {
    let view;
    const Spy = () => {
      view = useContext(Location);
      return null;
    };
    const history = {
      location: {
        pathname: '/kg/waterwolf/path/',
        search: '?status=missing,warnings&list=13,42,99&string=42',
      },
      listen: vi.fn(),
    };
    render(
      <LocationProvider history={history}>
        <Spy />
      </LocationProvider>,
    );
    expect(view).toMatchObject({
      locale: 'kg',
      project: 'waterwolf',
      resource: 'path',
      entity: 42,
      list: [13, 42, 99],
      status: null,
    });
  });
});
