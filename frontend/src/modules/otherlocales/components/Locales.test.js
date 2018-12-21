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
        const wrapper = shallow(
            <Locales otherlocales={ otherlocales } parameters={ params } />
        );

        expect(wrapper.find('li')).toHaveLength(3);
    });

    it('returns null while otherlocales are loading', () => {
        const otherlocales = {
            fetching: true,
        };
        const wrapper = shallow(<Locales otherlocales={ otherlocales } />);

        expect(wrapper.type()).toBeNull();
    });

    it('renders a no results message if otherlocales is empty', () => {
        const otherlocales = {
            fetching: false,
            translations: [],
        };
        const wrapper = shallow(<Locales otherlocales={ otherlocales } />);

        expect(wrapper.find('#history-history-no-translations')).toHaveLength(1);
    });
});
