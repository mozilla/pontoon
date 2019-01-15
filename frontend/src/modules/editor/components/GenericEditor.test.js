import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import GenericEditor from './GenericEditor';


describe('<GenericEditor>', () => {
    it('renders a textarea with some content', () => {
        const wrapper = shallow(<GenericEditor translation='hello' />);

        expect(wrapper.find('textarea')).toHaveLength(1);
        expect(wrapper.find('textarea').html()).toContain('hello');
    });

    it('calls the updateTranslation function on change', () => {
        const mockUpdate = sinon.spy();
        const wrapper = shallow(<GenericEditor
            translation='hello'
            updateTranslation={ mockUpdate }
        />);

        expect(mockUpdate.called).toBeFalsy();
        wrapper.find('textarea').simulate('change', { currentTarget: { value: 'good bye' } });
        expect(mockUpdate.called).toBeTruthy();
    });
});
