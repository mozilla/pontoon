import React from 'react';
import { shallow } from 'enzyme';

import History from './History';


describe('<History>', () => {
    it('shows the correct number of translations', () => {
        const history = {
            translations: [
                { pk: 1 },
                { pk: 2 },
                { pk: 3 },
            ],
        };
        const wrapper = shallow(<History history={ history } />);

        expect(wrapper.find('Translation')).toHaveLength(3);
    });

    it('returns null while history is loading', () => {
        const history = {
            fetching: true,
        };
        const wrapper = shallow(<History history={ history } />);

        expect(wrapper.type()).toBeNull();
    });

    it('renders a no results message if history is empty', () => {
        const history = {
            fetching: false,
            translations: [],
        };
        const wrapper = shallow(<History history={ history } />);

        expect(wrapper.find('#history-history-no-translations')).toHaveLength(1);
    });
});
