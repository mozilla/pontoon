import { shallow } from 'enzyme';
import React from 'react';
import { FluentAttribute } from './FluentAttribute';

describe('isSimpleSingleAttributeMessage', () => {
  it('renders nonempty for a string with a single attribute', () => {
    const original = 'my-entry =\n    .an-atribute = Hello!';
    const wrapper = shallow(
      <FluentAttribute entity={{ format: 'ftl', original }} />,
    );
    expect(wrapper.isEmptyRender()).toEqual(false);
  });

  it('renders null for string with value', () => {
    const original = 'my-entry = Something\n    .an-atribute = Hello!';
    const wrapper = shallow(
      <FluentAttribute entity={{ format: 'ftl', original }} />,
    );
    expect(wrapper.isEmptyRender()).toEqual(true);
  });

  it('renders null for string with several attributes', () => {
    const original =
      'my-entry =\n    .an-atribute = Hello!\n    .two-attrites = World!';
    const wrapper = shallow(
      <FluentAttribute entity={{ format: 'ftl', original }} />,
    );
    expect(wrapper.isEmptyRender()).toEqual(true);
  });
});
