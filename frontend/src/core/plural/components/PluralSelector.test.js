import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

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
                    pathname: '/kg/pro/all/',
                    search: '?string=42',
                },
            },
        };
        const store = createReduxStore(initialState);
        const dispatchSpy = sinon.spy(store, 'dispatch');

        const wrapper = shallowUntilTarget(
            <PluralSelector store={store} resetEditor={sinon.spy()} />,
            PluralSelectorBase,
        );

        wrapper.find('button').first().simulate('click');

        const expectedAction = actions.select(0);
        expect(dispatchSpy.calledWith(expectedAction)).toBeTruthy();
    });
});
