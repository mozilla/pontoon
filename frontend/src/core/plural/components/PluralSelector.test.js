import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions } from '..';

import PluralSelector, { PluralSelectorBase } from './PluralSelector';


function createShallowPluralSelector(plural, locale) {
    return shallow(<PluralSelectorBase
        pluralForm={ plural }
        locale={ locale }
    />);
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
        const wrapper = createShallowPluralSelector(-1, { cldrPlurals: [1, 5] });
        expect(wrapper.type()).toBeNull();
    });

    it('shows the correct list of plural choices for locale with 2 forms', () => {
        const wrapper = createShallowPluralSelector(0, { cldrPlurals: [1, 5] });

        const liElts = wrapper.find('li');
        expect(liElts).toHaveLength(2);
        expect(liElts.at(0).find('#plural-selector-form-one')).toHaveLength(1);
        expect(liElts.at(0).text()).toContain('1');
        expect(liElts.at(1).find('#plural-selector-form-other')).toHaveLength(1);
        expect(liElts.at(1).text()).toContain('2');
    });

    it('shows the correct list of plural choices for locale with all 6 forms', () => {
        const wrapper = createShallowPluralSelector(
            0,
            {
                cldrPlurals: [0, 1, 2, 3, 4, 5],
                // This is the pluralRule for Arabic.
                pluralRule: '(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5)'
            },
        );

        expect(wrapper.find('li')).toHaveLength(6);

        const pluralsAndExamples = [
            ['zero', '0'],
            ['one', '1'],
            ['two', '2'],
            ['few', '3'],
            ['many', '11'],
            ['other', '100'],
        ];
        wrapper.find('li').forEach((node, index) => {
            const [ form, example ] = pluralsAndExamples[index];
            expect(node.find(`#plural-selector-form-${form}`)).toHaveLength(1);
            expect(node.text()).toContain(example);
        });
    });

    it('marks the right choice as active', () => {
        const wrapper = createShallowPluralSelector(1, { cldrPlurals: [1, 5] });

        expect(wrapper.find('li.active').find(`#plural-selector-form-other`)).toHaveLength(1);
        expect(wrapper.find('li.active').text()).toContain('2');
    });
});


describe('<PluralSelector>', () => {
    it('selects the correct form when clicking a choice', () => {
        const initialState = {
            plural: {
                pluralForm: 1,
            },
            locales: {
                locales: {
                    'kg': {
                        cldrPlurals: [1, 5],
                    }
                },
            },
            router: {
                location: {
                    pathname: '/kg/pro/all/',
                    search: '?string=42',
                }
            },
        }
        const store = createReduxStore(initialState);
        const dispatchSpy = sinon.spy(store, 'dispatch');

        const wrapper = shallowUntilTarget(
            <PluralSelector store={ store } />,
            PluralSelectorBase
        );

        wrapper.find('button').first().simulate('click');

        const expectedAction = actions.select(0);
        expect(dispatchSpy.calledWith(expectedAction)).toBeTruthy();
    });
});
