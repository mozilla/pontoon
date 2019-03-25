import React from 'react';
import { shallow } from 'enzyme';

import WithPlaceablesNoUnusualSpace from './WithPlaceablesNoUnusualSpace';


describe('<WithPlaceablesNoUnusualSpace>', () => {
    it('matches newlines in a string', () => {
        const content = 'Hello\nworld';
        const wrapper = shallow(<WithPlaceablesNoUnusualSpace>
            { content }
        </WithPlaceablesNoUnusualSpace>);

        expect(wrapper.find('mark')).toHaveLength(1);
        expect(wrapper.find('mark').text()).toContain('\n');
    });

    it('does not match spaces at the beginning of a string', () => {
        const content = ' Hello world';
        const wrapper = shallow(<WithPlaceablesNoUnusualSpace>
            { content }
        </WithPlaceablesNoUnusualSpace>);

        expect(wrapper.text()).toEqual(content);
    });
});
