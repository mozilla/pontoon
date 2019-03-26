import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import GenericEditor from './GenericEditor';


const DEFAULT_LOCALE = {
    direction: 'ltr',
    code: 'kg',
    script: 'Latin',
};


describe('<GenericEditor>', () => {
    it('renders a textarea with some content', () => {
        const wrapper = shallow(<GenericEditor
            translation='hello'
            locale={ DEFAULT_LOCALE }
        />);

        expect(wrapper.find('textarea')).toHaveLength(1);
        expect(wrapper.find('textarea').html()).toContain('hello');
    });

    it('calls the updateTranslation function on change', () => {
        const mockUpdate = sinon.spy();
        const wrapper = shallow(<GenericEditor
            translation='hello'
            locale={ DEFAULT_LOCALE }
            updateTranslation={ mockUpdate }
        />);

        expect(mockUpdate.called).toBeFalsy();
        wrapper.find('textarea').simulate('change', { currentTarget: { value: 'good bye' } });
        expect(mockUpdate.called).toBeTruthy();
    });

    it('updates the translation when selectionReplacementContent is passed', () => {
        const resetMock = sinon.stub();
        const updateMock = sinon.stub();

        const wrapper = mount(<GenericEditor
            translation='hello'
            locale={ DEFAULT_LOCALE }
            resetSelectionContent={ resetMock }
            updateTranslation={ updateMock }
        />);

        wrapper.setProps({ editor: { selectionReplacementContent: ' world' } });

        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith('hello world')).toBeTruthy();
        expect(resetMock.calledOnce).toBeTruthy();
    });
});
