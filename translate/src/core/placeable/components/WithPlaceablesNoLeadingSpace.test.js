import React from 'react';
import { shallow } from 'enzyme';

import WithPlaceablesNoLeadingSpace from './WithPlaceablesNoLeadingSpace';

describe('<WithPlaceablesNoLeadingSpace>', () => {
    it('matches newlines in a string', () => {
        const content = 'Hello\nworld';
        const wrapper = shallow(
            <WithPlaceablesNoLeadingSpace>
                {content}
            </WithPlaceablesNoLeadingSpace>,
        );

        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toContain('\n');
    });

    it('does not match spaces at the beginning of a string', () => {
        const content = ' Hello world';
        const wrapper = shallow(
            <WithPlaceablesNoLeadingSpace>
                {content}
            </WithPlaceablesNoLeadingSpace>,
        );

        expect(wrapper.text()).toEqual(content);
    });
});
