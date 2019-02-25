import React from 'react';
import { shallow } from 'enzyme';

import Locales from './Locales';


describe('<Locales>', () => {
    it('shows the correct number of translations', () => {
        const otherlocales = {
            translations: [
                { code: 'ar' },
                { code: 'br' },
                { code: 'cr' },
            ],
        };
        const params = {
            locale: 'kg',
            project: 'tmo',
        };
        const user = {}
        const wrapper = shallow(
            <Locales
                otherlocales={ otherlocales }
                parameters={ params }
                user={ user }
            />
        );

        expect(wrapper.find('Translation')).toHaveLength(3);
    });

    it('shows preferred locales first', () => {
        const otherlocales = {
            translations: [
                { code: 'ar' },
                { code: 'br' },
                { code: 'cr' },
            ],
        };
        const params = {
            locale: 'kg',
            project: 'tmo',
        };
        const user = {
            isAuthenticated: true,
            preferredLocales: ['ab', 'br', 'cd']
        };
        const wrapper = shallow(
            <Locales
                otherlocales={ otherlocales }
                parameters={ params }
                user={ user }
            />
        );

        expect(wrapper.find('Translation:first-child .stress').text()).toContain('br');
    });

    it('returns null while otherlocales are loading', () => {
        const otherlocales = {
            fetching: true,
        };
        const user = {}
        const wrapper = shallow(<Locales
            otherlocales={ otherlocales }
            user={ user }
        />);

        expect(wrapper.type()).toBeNull();
    });

    it('renders a no results message if otherlocales is empty', () => {
        const otherlocales = {
            fetching: false,
            translations: [],
        };
        const user = {}
        const wrapper = shallow(<Locales
            otherlocales={ otherlocales }
            user={ user }
        />);

        expect(wrapper.find('#history-history-no-translations')).toHaveLength(1);
    });
});
