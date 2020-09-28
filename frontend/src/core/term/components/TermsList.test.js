import React from 'react';
import { shallow } from 'enzyme';

import Term from './Term';
import TermsList from './TermsList';

describe('<TermsList>', () => {
    const TERMS = [
        {
            text: 'text1',
        },
        {
            text: 'text2',
        },
        {
            text: 'text3',
        },
    ];

    it('renders list of terms correctly', () => {
        const wrapper = shallow(<TermsList terms={TERMS} />);

        expect(wrapper.find(Term)).toHaveLength(3);
    });
});
