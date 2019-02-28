import React from 'react';
import { shallow } from 'enzyme';

import OtherLocales from './OtherLocales';


describe('<OtherLocales>', () => {
    it('shows the correct number of translations', () => {
        const otherlocales = {
            translations: [
                { code: 'ar' },
                { code: 'br' },
                { code: 'cr' },
            ],
        };
        const orderedOtherLocales = [
            { code: 'br' },
            { code: 'ar' },
            { code: 'cr' },
        ];
        const params = {
            locale: 'kg',
            project: 'tmo',
        };
        const user = {}
        const wrapper = shallow(
            <OtherLocales
                otherlocales={ otherlocales }
                orderedOtherLocales={ orderedOtherLocales }
                parameters={ params }
                user={ user }
            />
        );

        expect(wrapper.find('Translation')).toHaveLength(3);
    });

    it('returns null while otherlocales are loading', () => {
        const otherlocales = {
            fetching: true,
        };
        const user = {}
        const wrapper = shallow(<OtherLocales
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
        const wrapper = shallow(<OtherLocales
            otherlocales={ otherlocales }
            user={ user }
        />);

        expect(wrapper.find('#history-history-no-translations')).toHaveLength(1);
    });
});
