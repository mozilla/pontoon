import { shallow } from 'enzyme';
import React, { useContext } from 'react';
import sinon from 'sinon';

import { Locale } from '~/context/locale';
import { PluralForm, PluralFormProvider } from '~/context/pluralForm';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { PluralSelector, PluralSelectorBase } from './PluralSelector';

const createShallowPluralSelector = (pluralForm) =>
  shallow(
    <PluralSelectorBase
      pluralForm={{ pluralForm }}
      resetEditor={sinon.spy()}
    />,
  );

describe('<PluralSelectorBase>', () => {
  beforeAll(() =>
    sinon.stub(React, 'useContext').returns({ code: 'mylocale' }),
  );
  afterAll(() => React.useContext.restore());

  it('returns null when the locale is missing', () => {
    React.useContext.returns({ cldrPlurals: [] });
    const wrapper = createShallowPluralSelector(0);
    expect(wrapper.type()).toBeNull();
  });

  it('returns null when the locale has only one plural form', () => {
    React.useContext.returns({ cldrPlurals: [5] });
    const wrapper = createShallowPluralSelector(0);
    expect(wrapper.type()).toBeNull();
  });

  it('returns null when the selected plural form is -1', () => {
    React.useContext.returns({ cldrPlurals: [1, 5] });
    // If pluralForm is -1, it means the entity has no plural string.
    const wrapper = createShallowPluralSelector(-1);
    expect(wrapper.type()).toBeNull();
  });

  it('shows the correct list of plural choices for locale with 2 forms', () => {
    React.useContext.returns({ cldrPlurals: [1, 5] });
    const wrapper = createShallowPluralSelector(0);

    expect(wrapper.find('li')).toHaveLength(2);
    expect(wrapper.find('ul').text()).toEqual('one1other2');
  });

  it('shows the correct list of plural choices for locale with all 6 forms', () => {
    // This is the pluralRule for Arabic.
    React.useContext.returns({
      cldrPlurals: [0, 1, 2, 3, 4, 5],
      pluralRule:
        '(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5)',
    });
    const wrapper = createShallowPluralSelector(0);

    expect(wrapper.find('li')).toHaveLength(6);
    expect(wrapper.find('ul').text()).toEqual(
      'zero0one1two2few3many11other100',
    );
  });

  it('marks the right choice as active', () => {
    React.useContext.returns({ cldrPlurals: [1, 5] });
    const wrapper = createShallowPluralSelector(1);

    expect(wrapper.find('li.active').text()).toEqual('other2');
  });
});

describe('<PluralSelector>', () => {
  it('selects the correct form when clicking a choice', () => {
    const store = createReduxStore({
      entities: { entities: [{ pk: 0, original_plural: 'exists' }] },
    });

    const pfLog = [];
    const Spy = () => {
      pfLog.push(useContext(PluralForm).pluralForm);
      return null;
    };
    const Component = () => (
      <PluralFormProvider>
        <Spy />
        <Locale.Provider value={{ code: 'kg', cldrPlurals: [1, 5] }}>
          <PluralSelector resetEditor={sinon.spy()} />
        </Locale.Provider>
      </PluralFormProvider>
    );
    const wrapper = mountComponentWithStore(Component, store);
    wrapper.find('li:last-child button').simulate('click', {});

    expect(pfLog).toEqual([-1, 1]);
  });
});
