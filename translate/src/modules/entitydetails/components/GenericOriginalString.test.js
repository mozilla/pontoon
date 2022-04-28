import { mount } from 'enzyme';
import React from 'react';

import { Locale } from '~/context/locale';

import { MockLocalizationProvider } from '~/test/utils';

import GenericOriginalString from './GenericOriginalString';

const ENTITY = {
  pk: 42,
  original: 'le test',
  original_plural: 'les tests',
};

const LOCALE = {
  code: 'kg',
  cldrPlurals: [1, 3, 5],
};

const createGenericOriginalString = (pluralForm = -1) =>
  mount(
    <Locale.Provider value={LOCALE}>
      <MockLocalizationProvider>
        <GenericOriginalString
          entity={ENTITY}
          pluralForm={pluralForm}
          terms={{}}
        />
      </MockLocalizationProvider>
    </Locale.Provider>,
  );

describe('<GenericOriginalString>', () => {
  it('renders correctly', () => {
    const wrapper = createGenericOriginalString();

    const originalContent = wrapper.find('ContentMarker').props().children;
    expect(originalContent).toContain(ENTITY.original);
  });

  it('renders the selected plural form as original string', () => {
    const wrapper = createGenericOriginalString(2);

    expect(
      wrapper.find('#entitydetails-GenericOriginalString--plural'),
    ).toHaveLength(1);

    const originalContent = wrapper.find('ContentMarker').props().children;
    expect(originalContent).toContain(ENTITY.original_plural);
  });

  it('renders the selected singular form as original string', () => {
    const wrapper = createGenericOriginalString(0);

    expect(
      wrapper.find('#entitydetails-GenericOriginalString--singular'),
    ).toHaveLength(1);

    const originalContent = wrapper.find('ContentMarker').props().children;
    expect(originalContent).toContain(ENTITY.original);
  });
});
