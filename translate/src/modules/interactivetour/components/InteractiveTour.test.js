import { shallow } from 'enzyme';
import React from 'react';
import Tour from 'reactour';
import sinon from 'sinon';

import * as hookModule from '~/hooks/useTranslator';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { InteractiveTour } from './InteractiveTour';

beforeAll(() => sinon.stub(hookModule, 'useTranslator'));
beforeEach(() => hookModule.useTranslator.returns(false));
afterAll(() => hookModule.useTranslator.restore());

describe('<InteractiveTourBase>', () => {
  it('renders correctly on the tutorial page for unauthenticated user', () => {
    const store = createReduxStore({
      project: { slug: 'tutorial' },
      user: { isAuthenticated: false },
    });
    const wrapper = mountComponentWithStore(InteractiveTour, store);

    expect(wrapper.find(Tour)).toHaveLength(1);
  });

  it('does not render on non-tutorial page', () => {
    const store = createReduxStore({
      project: { slug: 'firefox' },
      user: { isAuthenticated: false },
    });
    const wrapper = mountComponentWithStore(InteractiveTour, store);

    expect(wrapper.find(Tour)).toHaveLength(0);
  });

  it('does not render if the user has already seen the tutorial', () => {
    const store = createReduxStore({
      project: { slug: 'tutorial' },
      user: { tourStatus: -1 },
    });
    const wrapper = mountComponentWithStore(InteractiveTour, store);

    expect(wrapper.find(Tour)).toHaveLength(0);
  });
});
