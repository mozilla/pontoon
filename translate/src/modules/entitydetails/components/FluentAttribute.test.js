import ftl from '@fluent/dedent';
import { shallow } from 'enzyme';
import React from 'react';
import { parseEntry } from '~/utils/message';
import { FluentAttribute } from './FluentAttribute';

describe('isSimpleSingleAttributeMessage', () => {
  it('renders nonempty for a string with a single attribute', () => {
    const original = ftl`
      my-entry =
          .an-atribute = Hello!
      `;
    const entry = parseEntry('fluent', original);
    const wrapper = shallow(<FluentAttribute entry={entry} />);
    expect(wrapper.isEmptyRender()).toEqual(false);
  });

  it('renders null for string with value', () => {
    const original = ftl`
      my-entry = Something
          .an-atribute = Hello!
      `;
    const entry = parseEntry('fluent', original);
    const wrapper = shallow(<FluentAttribute entry={entry} />);
    expect(wrapper.isEmptyRender()).toEqual(true);
  });

  it('renders null for string with several attributes', () => {
    const original = ftl`
      my-entry =
          .an-atribute = Hello!
          .two-attrites = World!
      `;
    const entry = parseEntry('fluent', original);
    const wrapper = shallow(<FluentAttribute entry={entry} />);
    expect(wrapper.isEmptyRender()).toEqual(true);
  });
});
