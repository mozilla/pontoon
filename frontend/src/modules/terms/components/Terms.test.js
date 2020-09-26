import React from 'react';
import { shallow } from 'enzyme';

import Terms from './Terms';
import { TermsList } from 'core/term';

describe('<Terms>', () => {
    it('returns null while terms are loading', () => {
        const terms = {
            fetching: true,
        };

        const wrapper = shallow(<Terms terms={terms} />);

        expect(wrapper.type()).toBeNull();
    });

    it('renders a no terms message when no terms are available', () => {
        const terms = {
            terms: [],
        };

        const wrapper = shallow(<Terms terms={terms} />);

        expect(wrapper.find('p').text()).toEqual('No terms available.');
    });

    it('renders terms list correctly', () => {
        const terms = {
            terms: [{}],
        };

        const wrapper = shallow(<Terms terms={terms} />);

        expect(wrapper.find('p')).toHaveLength(0);
        expect(wrapper.find(TermsList)).toHaveLength(1);
    });
});
