import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import FluentEditor from './FluentEditor';


describe('<FluentEditor>', () => {
    it('renders a textarea with some content', () => {
        const wrapper = shallow(<FluentEditor translation='hello' />);

        expect(wrapper.find('ReactAce')).toHaveLength(1);
    });

    it('updates the translation when selectionReplacementContent is passed', () => {
        const resetMock = sinon.stub();
        const updateMock = sinon.stub();

        const wrapper = mount(<FluentEditor
            translation='hello'
            resetSelectionContent={ resetMock }
            updateTranslation={ updateMock }
        />);

        wrapper.setProps({ editor: { selectionReplacementContent: ' world' } });

        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith('hello world')).toBeTruthy();
        expect(resetMock.calledOnce).toBeTruthy();
    });
});
