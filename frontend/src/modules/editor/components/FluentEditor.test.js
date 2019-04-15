import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import FluentEditor from './FluentEditor';


describe('<FluentEditor>', () => {
    const EDITOR = {
        translation: 'hello',
    };

    it('renders a textarea with some content', () => {
        const wrapper = shallow(<FluentEditor editor={ EDITOR } />);

        expect(wrapper.find('ReactAce')).toHaveLength(1);
    });

    it('updates the translation when selectionReplacementContent is passed', () => {
        const resetMock = sinon.stub();
        const updateMock = sinon.stub();

        const wrapper = mount(<FluentEditor
            editor={ EDITOR }
            resetSelectionContent={ resetMock }
            updateTranslation={ updateMock }
        />);

        wrapper.setProps({
            editor: {
                ...EDITOR,
                selectionReplacementContent: ' world'
            }
        });

        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith('hello world')).toBeTruthy();
        expect(resetMock.calledOnce).toBeTruthy();
    });
});
