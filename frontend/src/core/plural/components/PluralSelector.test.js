import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore, mountComponentWithStore } from 'test/store';

import { actions } from '..';

import PluralSelector, { PluralSelectorBase } from './PluralSelector';

function createShallowPluralSelector(plural, locale) {
    return shallow(
        <PluralSelectorBase
            pluralForm={plural}
            locale={locale}
            resetEditor={sinon.spy()}
        />,
    );
}

describe('<PluralSelectorBase>', () => {
    it('returns null when the locale is missing', () => {
        const wrapper = createShallowPluralSelector(0, null);
        expect(wrapper.type()).toBeNull();
    });

    it('returns null when the locale has only one plural form', () => {
        const wrapper = createShallowPluralSelector(0, { cldrPlurals: [5] });
        expect(wrapper.type()).toBeNull();
    });

    it('returns null when the selected plural form is -1', () => {
        // If pluralForm is -1, it means the entity has no plural string.
        const wrapper = createShallowPluralSelector(-1, {
            cldrPlurals: [1, 5],
        });
        expect(wrapper.type()).toBeNull();
    });

    it('shows the correct list of plural choices for locale with 2 forms', () => {
        const wrapper = createShallowPluralSelector(0, { cldrPlurals: [1, 5] });

        expect(wrapper.find('li')).toHaveLength(2);
        expect(wrapper.find('ul').text()).toEqual('one1other2');
    });

    it('shows the correct list of plural choices for locale with all 6 forms', () => {
        const wrapper = createShallowPluralSelector(0, {
            cldrPlurals: [0, 1, 2, 3, 4, 5],
            // This is the pluralRule for Arabic.
            pluralRule:
                '(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5)',
        });

        expect(wrapper.find('li')).toHaveLength(6);
        expect(wrapper.find('ul').text()).toEqual(
            'zero0one1two2few3many11other100',
        );
    });

    it('marks the right choice as active', () => {
        const wrapper = createShallowPluralSelector(1, { cldrPlurals: [1, 5] });

        expect(wrapper.find('li.active').text()).toEqual('other2');
    });
});

describe('<PluralSelector>', () => {
    it('selects the correct form when clicking a choice', () => {
        const initialState = {
            plural: {
                pluralForm: 1,
            },
            locale: {
                code: 'kg',
                cldrPlurals: [1, 5],
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

        const root = mountComponentWithStore(PluralSelector, store, {
            resetEditor: sinon.spy(),
        });
        const wrapper = root.find(PluralSelectorBase);

        const button = wrapper.find('button').first();
        // `simulate()` doesn't quite work in conjunction with `mount()`, so
        // invoking the `prop()` callback directly is the way to go as suggested
        // by the enzyme maintainer...
        button.prop('onClick')();

        const expectedAction = actions.select(0);
        expect(dispatchSpy.calledWith(expectedAction)).toBeTruthy();
    });
});
