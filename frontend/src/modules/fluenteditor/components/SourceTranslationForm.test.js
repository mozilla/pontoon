import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import SourceTranslationForm from './SourceTranslationForm';


describe('<SourceTranslationForm>', () => {
    const EDITOR = {
        translation: 'world',
    };

    it('renders ReactAce editor with some content', () => {
        const wrapper = shallow(<SourceTranslationForm editor={ EDITOR } />);

        expect(wrapper.find('ReactAce')).toHaveLength(1);
    });

    it('updates the translation when selectionReplacementContent is passed', () => {
        const resetMock = sinon.stub();
        const updateMock = sinon.stub();

        const wrapper = mount(<SourceTranslationForm
            editor={ EDITOR }
            resetSelectionContent={ resetMock }
            updateTranslation={ updateMock }
        />);

        wrapper.setProps({
            editor: {
                ...EDITOR,
                selectionReplacementContent: 'hello '
            }
        });

        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith('hello world')).toBeTruthy();
        expect(resetMock.calledOnce).toBeTruthy();
    });
});
