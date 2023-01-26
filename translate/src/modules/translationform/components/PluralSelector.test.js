import { mount } from 'enzyme';
import React from 'react';

import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';

import { PluralSelector } from './PluralSelector';

function mountPluralSelector(
  cldrPlurals,
  hasPluralForms = false,
  setPluralForm = () => {},
  pluralRule = '',
) {
  return mount(
    <EntityView.Provider
      value={{ hasPluralForms, pluralForm: 0, setPluralForm }}
    >
      <Locale.Provider value={{ code: 'kg', cldrPlurals, pluralRule }}>
        <PluralSelector />
      </Locale.Provider>
    </EntityView.Provider>,
  );
}

describe('<PluralSelector>', () => {
  it('returns null when the locale is missing', () => {
    const wrapper = mountPluralSelector([]);

    expect(wrapper.find('PluralSelector').isEmptyRender()).toBeTruthy();
  });

  it('returns null when the locale has only one plural form', () => {
    const wrapper = mountPluralSelector([5]);

    expect(wrapper.find('PluralSelector').isEmptyRender()).toBeTruthy();
  });

  it('returns null when hasPluralForms is false', () => {
    const wrapper = mountPluralSelector([1, 5]);
    wrapper.update();

    expect(wrapper.find('PluralSelector').isEmptyRender()).toBeTruthy();
  });

  it('shows the correct list of plural choices for locale with 2 forms', () => {
    const wrapper = mountPluralSelector([1, 5], true);

    expect(wrapper.find('li')).toHaveLength(2);
    expect(wrapper.find('ul').text()).toEqual('one1other2');
  });

  it('shows the correct list of plural choices for locale with all 6 forms', () => {
    // This is the pluralRule for Arabic.
    const wrapper = mountPluralSelector(
      [0, 1, 2, 3, 4, 5],
      true,
      () => {},
      '(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5)',
    );

    expect(wrapper.find('li')).toHaveLength(6);
    expect(wrapper.find('ul').text()).toEqual(
      'zero0one1two2few3many11other100',
    );
  });

  it('selects the correct form when clicking a choice', () => {
    const spy = jest.fn();
    const wrapper = mountPluralSelector([1, 5], true, spy);
    wrapper.find('li:last-child button').simulate('click', {});

    expect(spy.mock.calls).toEqual([[1]]);
  });
});
