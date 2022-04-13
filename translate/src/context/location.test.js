import { shallow } from 'enzyme';
import React from 'react';

import { LocationProvider } from './location';

describe('LocationProvider', () => {
  it('correctly parses the pathname', () => {
    const history = {
      location: { pathname: '/kg/waterwolf/path/to/RESOURCE.po/', search: '' },
    };
    const wrapper = shallow(<LocationProvider history={history} />);

    expect(wrapper.prop('value')).toMatchObject({
      locale: 'kg',
      project: 'waterwolf',
      resource: 'path/to/RESOURCE.po',
      entity: 0,
      status: null,
    });
  });

  it('correctly parses the query string', () => {
    const history = {
      location: {
        pathname: '/kg/waterwolf/path/',
        search: '?status=missing,warnings&string=42',
      },
    };
    const wrapper = shallow(<LocationProvider history={history} />);

    expect(wrapper.prop('value')).toMatchObject({
      locale: 'kg',
      project: 'waterwolf',
      resource: 'path',
      entity: 42,
      status: 'missing,warnings',
    });
  });
});
