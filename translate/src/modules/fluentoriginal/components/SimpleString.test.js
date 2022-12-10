import ftl from '@fluent/dedent';
import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { SimpleString } from './SimpleString';

const ENTITY = {
  format: 'ftl',
  original: ftl`
    header =
        .page-title = Hello
        Simple
        String
    `,
};

describe('<SimpleString>', () => {
  it('renders original input as simple string', () => {
    const wrapper = shallow(<SimpleString entity={ENTITY} terms={{}} />);

    expect(wrapper.find('.original').children().children().text()).toEqual(
      'Hello\nSimple\nString',
    );
  });

  it('calls the handleClickOnPlaceable function on click on .original', () => {
    const handleClickOnPlaceable = sinon.spy();
    const wrapper = shallow(
      <SimpleString
        entity={ENTITY}
        handleClickOnPlaceable={handleClickOnPlaceable}
        terms={{}}
      />,
    );

    wrapper.find('.original').simulate('click');
    expect(handleClickOnPlaceable.called).toEqual(true);
  });
});
