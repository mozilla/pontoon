import { shallow } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import { Locale } from '~/context/locale';
import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { actions } from '..';

import PluralSelector, { PluralSelectorBase } from './PluralSelector';

const createShallowPluralSelector = (plural) =>
  shallow(<PluralSelectorBase pluralForm={plural} resetEditor={sinon.spy()} />);

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
    const initialState = {
      plural: {
        pluralForm: 1,
      },
      router: {
        location: {
          pathname: '/kg/firefox/all-resources/',
          search: '?string=42',
        },
        // `action` is required because
        // https://github.com/supasate/connected-react-router/issues/312#issuecomment-500968504
        // Please note the initial `LOCATION_CHANGE` action can and must
        // be supressed via the `noInitialPop` prop in
        // `ConnectedRouter`, otherwise it'll cause side-effects like
        // executing reducers and hence altering initial state values.
        action: 'some-string-to-please-connected-react-router',
      },
    };
    const store = createReduxStore(initialState);
    const dispatchSpy = sinon.spy(store, 'dispatch');

    const Component = () => (
      <Locale.Provider value={{ code: 'kg', cldrPlurals: [1, 5] }}>
        <PluralSelector resetEditor={sinon.spy()} />
      </Locale.Provider>
    );
    const wrapper = mountComponentWithStore(Component, store);

    const button = wrapper.find('button').first();
    // `simulate()` doesn't quite work in conjunction with `mount()`, so
    // invoking the `prop()` callback directly is the way to go as suggested
    // by the enzyme maintainer...
    button.prop('onClick')();

    const expectedAction = actions.select(0);
    expect(dispatchSpy.calledWith(expectedAction)).toBeTruthy();
  });
});
