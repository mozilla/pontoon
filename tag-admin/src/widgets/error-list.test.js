import { mount } from 'enzyme';
import React from 'react';

import { ErrorList } from './error-list.js';

test('ErrorList render', () => {
  const errors = mount(<ErrorList errors={{}} />);
  expect(errors.text()).toBe('');
  expect(errors.find('ul').length).toBe(0);

  errors.setProps({ errors: { foo: 'Did a foo', bar: 'Bars happen' } });
  expect(errors.find('ul.errors')).toHaveLength(1);
  expect(errors.find('li.error')).toHaveLength(2);
  expect(errors.find('li.error').at(1).html()).toBe(
    '<li class="error">bar: Bars happen</li>',
  );
});
