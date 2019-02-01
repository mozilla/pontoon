import React from 'react';
import { shallow } from 'enzyme';

import { MachineryBase } from './Machinery';


describe('<Machinery>', () => {
    const LOCALE = {
        code: 'kg',
    };

    it('shows a search form', () => {
        const machinery = {
            translations: [],
        };
        const wrapper = shallow(<MachineryBase machinery={ machinery } locale={ LOCALE } />);

        expect(wrapper.find('.search-wrapper')).toHaveLength(1);
        expect(wrapper.find('#machinery-machinery-search-placeholder')).toHaveLength(1);
    });

    it('shows the correct number of translations', () => {
        const machinery = {
            translations: [
                { original: '1' },
                { original: '2' },
                { original: '3' },
            ],
        };
        const wrapper = shallow(<MachineryBase machinery={ machinery } locale={ LOCALE } />);

        expect(wrapper.find('Translation')).toHaveLength(3);
    });

    it('returns null if there is no locale', () => {
        const wrapper = shallow(<MachineryBase locale={ null } />);
        expect(wrapper.type()).toBeNull();
    });
});
