import { shallow } from 'enzyme';
import React from 'react';
import Tour from 'reactour';
import sinon from 'sinon';

import * as hookModule from '~/hooks/useTranslator';
import { InteractiveTourBase } from './InteractiveTour';

beforeAll(() => sinon.stub(hookModule, 'useTranslator'));
beforeEach(() => hookModule.useTranslator.returns(false));
afterAll(() => hookModule.useTranslator.restore());

describe('<InteractiveTourBase>', () => {
  it('renders correctly on the tutorial page for unauthenticated user', () => {
    const wrapper = shallow(
      <InteractiveTourBase
        locale={{ code: 'lc' }}
        project={{ slug: 'tutorial' }}
        user={{ isAuthenticated: false }}
      />,
    );

    expect(wrapper.find(Tour)).toHaveLength(1);
  });

  it('does not render on non-tutorial page', () => {
    const wrapper = shallow(
      <InteractiveTourBase
        locale={{ code: 'lc' }}
        project={{ slug: 'firefox' }}
        user={{ isAuthenticated: false }}
      />,
    );

    expect(wrapper.find(Tour)).toHaveLength(0);
  });

  it('does not render if the user has already seen the tutorial', () => {
    const wrapper = shallow(
      <InteractiveTourBase
        locale={{ code: 'lc' }}
        project={{ slug: 'tutorial' }}
        // the user has seen the tutorial
        user={{ tourStatus: -1 }}
      />,
    );

    expect(wrapper.find(Tour)).toHaveLength(0);
  });
});
