import React from 'react';
import { shallow } from 'enzyme';

import FluentEditor from './FluentEditor';


describe('<FluentEditor>', () => {
    it('renders a textarea with some content', () => {
        const wrapper = shallow(<FluentEditor translation='hello' />);

        expect(wrapper.find('ReactAce')).toHaveLength(1);
    });
});
