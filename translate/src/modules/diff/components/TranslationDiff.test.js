import React from 'react';
import { mount } from 'enzyme';

import { TranslationDiff } from './TranslationDiff';

describe('<TranslationDiff>', () => {
  it('returns the correct diff for provided strings', () => {
    const wrapper = mount(
      <TranslationDiff base={'abcdef'} target={'cdefgh'} />,
    );

    expect(wrapper.find('ins')).toHaveLength(1);
    expect(wrapper.find('del')).toHaveLength(1);
    expect(wrapper.childAt(1).text()).toEqual('cdef');
  });

  it('returns the same string if provided strings are equal', () => {
    const wrapper = mount(
      <TranslationDiff base={'abcdef'} target={'abcdef'} />,
    );

    expect(wrapper.find('ins')).toHaveLength(0);
    expect(wrapper.find('del')).toHaveLength(0);
    expect(wrapper.text()).toEqual('abcdef');
  });
});
