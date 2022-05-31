import React, { useEffect } from 'react';

import { Locale } from '~/context/Locale';
import { PluralFormProvider, usePluralForm } from '~/context/PluralForm';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { PluralSelector } from './PluralSelector';

function mountPluralSelector(
  pluralForm,
  cldrPlurals,
  original_plural = 'exists',
  pluralRule = '',
) {
  const store = createReduxStore({
    entities: { entities: [{ pk: 0, original_plural }] },
  });

  const pfLog = [];
  const Spy = () => {
    const pf = usePluralForm();
    pfLog.push(pf.pluralForm);
    useEffect(() => {
      pf.setPluralForm(pluralForm);
    }, []);
    return null;
  };
  const Component = () => (
    <PluralFormProvider>
      <Spy />
      <Locale.Provider value={{ code: 'kg', cldrPlurals, pluralRule }}>
        <PluralSelector />
      </Locale.Provider>
    </PluralFormProvider>
  );
  const wrapper = mountComponentWithStore(Component, store);
  return [wrapper, pfLog];
}

describe('<PluralSelector>', () => {
  it('returns null when the locale is missing', () => {
    const [wrapper] = mountPluralSelector(0, []);

    expect(wrapper.find('PluralSelector').isEmptyRender()).toBeTruthy();
  });

  it('returns null when the locale has only one plural form', () => {
    const [wrapper] = mountPluralSelector(0, [5]);

    expect(wrapper.find('PluralSelector').isEmptyRender()).toBeTruthy();
  });

  it('returns null when the selected plural form is -1', () => {
    // If pluralForm is -1, it means the entity has no plural string.
    const [wrapper] = mountPluralSelector(-1, [1, 5], null);
    wrapper.update();

    expect(wrapper.find('PluralSelector').isEmptyRender()).toBeTruthy();
  });

  it('shows the correct list of plural choices for locale with 2 forms', () => {
    const [wrapper] = mountPluralSelector(0, [1, 5]);

    expect(wrapper.find('li')).toHaveLength(2);
    expect(wrapper.find('ul').text()).toEqual('one1other2');
  });

  it('shows the correct list of plural choices for locale with all 6 forms', () => {
    // This is the pluralRule for Arabic.
    const [wrapper] = mountPluralSelector(
      0,
      [0, 1, 2, 3, 4, 5],
      'exists',
      '(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5)',
    );

    expect(wrapper.find('li')).toHaveLength(6);
    expect(wrapper.find('ul').text()).toEqual(
      'zero0one1two2few3many11other100',
    );
  });

  it('selects the correct form when clicking a choice', () => {
    const [wrapper, pfLog] = mountPluralSelector(0, [1, 5]);
    wrapper.find('li:last-child button').simulate('click', {});

    expect(pfLog).toEqual([-1, 1]);
    expect(wrapper.find('li.active').text()).toEqual('other2');
  });
});
