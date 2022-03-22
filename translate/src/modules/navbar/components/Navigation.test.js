import { shallow } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import { NavigationBase } from './Navigation';

describe('<Navigation>', () => {
  const LOCALE = {
    code: 'kg',
    name: 'Klingon',
  };
  const PROJECT = {
    name: 'Mark 42',
  };
  const PARAMETERS = {
    locale: 'kg',
    project: 'mark42',
    resource: 'stuff.ftl',
  };

  beforeAll(() => sinon.stub(React, 'useContext').returns(LOCALE));
  afterAll(() => React.useContext.restore());

  it('shows navigation', () => {
    const wrapper = shallow(
      <NavigationBase parameters={PARAMETERS} project={PROJECT} />,
    );

    expect(wrapper.text()).toContain('Klingon');
    expect(wrapper.text()).toContain('kg');
  });
});
