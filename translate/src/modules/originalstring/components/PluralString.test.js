import { mount } from 'enzyme';
import React from 'react';

import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';

import { MockLocalizationProvider } from '~/test/utils';

import { PluralString } from './PluralString';

const ENTITY = {
  pk: 42,
  original: 'le test',
  original_plural: 'les tests',
};

const LOCALE = {
  code: 'kg',
  cldrPlurals: [1, 3, 5],
};

const mountPluralString = (pluralForm) =>
  mount(
    <Locale.Provider value={LOCALE}>
      <MockLocalizationProvider>
        <EntityView.Provider
          value={{ entity: ENTITY, hasPluralForms: true, pluralForm }}
        >
          <PluralString terms={{}} />
        </EntityView.Provider>
      </MockLocalizationProvider>
    </Locale.Provider>,
  );

describe('<PluralString>', () => {
  it('renders the selected plural form as original string', () => {
    const wrapper = mountPluralString(2);

    expect(wrapper.find('#entitydetails-PluralString--plural')).toHaveLength(1);

    const originalContent = wrapper.find('.original > *').props().children;
    expect(originalContent).toContain(ENTITY.original_plural);
  });

  it('renders the selected singular form as original string', () => {
    const wrapper = mountPluralString(0);

    expect(wrapper.find('#entitydetails-PluralString--singular')).toHaveLength(
      1,
    );

    const originalContent = wrapper.find('.original > *').props().children;
    expect(originalContent).toContain(ENTITY.original);
  });
});
