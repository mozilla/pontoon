import { mount } from 'enzyme';
import React from 'react';

import { Checkbox } from './checkbox.js';

test('Checkbox render', () => {
  const checkbox = mount(<Checkbox id='x' />);
  expect(checkbox.find('input[type="checkbox"]#x')).toHaveLength(1);
});

test('Checkbox indeterminate', () => {
  const checkbox = mount(<Checkbox indeterminate />);
  expect(checkbox.getDOMNode().indeterminate).toBe(true);
});

test('Checkbox switch', () => {
  const checkbox = mount(<Checkbox indeterminate={0} />);
  expect(checkbox.getDOMNode().indeterminate).toBe(false);

  checkbox.setProps({ indeterminate: 1 });
  expect(checkbox.getDOMNode().indeterminate).toBe(true);
});
