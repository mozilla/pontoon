import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import Editor from './Editor';


const TRANSLATION = 'test';
const TRANSLATION_PLURAL = 'test plural';
const SELECTED_ENTITY = {
    pk: 42,
    original: 'le test',
    original_plural: 'les tests',
    translation: [
        { string: TRANSLATION },
        { string: TRANSLATION_PLURAL },
    ],
};


function createShallowEditor(suggestMock = null, pluralForm = -1) {
    return shallow(<Editor
        translation={ (Math.abs(pluralForm) !== 1) ? TRANSLATION_PLURAL : TRANSLATION }
        entity={ SELECTED_ENTITY }
        sendSuggestion={ suggestMock }
        pluralForm={ pluralForm }
    />);
}


describe('<Editor>', () => {
    it('renders correctly', () => {
        const wrapper = createShallowEditor();

        // 3 buttons to control the editor, 1 button for settings.
        expect(wrapper.find('button')).toHaveLength(4);
    });

    it('clears the text when the Clear button is clicked', () => {
        const wrapper = createShallowEditor();

        expect(wrapper.state('translation')).toEqual(TRANSLATION);
        wrapper.find('.action-clear').simulate('click');
        expect(wrapper.state('translation')).toEqual('');
    });

    it('copies the original string in the textarea when the Copy button is clicked', () => {
        const wrapper = createShallowEditor();

        expect(wrapper.state('translation')).toEqual(TRANSLATION);
        wrapper.find('.action-copy').simulate('click');
        expect(wrapper.state('translation')).toEqual(SELECTED_ENTITY.original);
    });

    it('copies the plural original string in the textarea when the Copy button is clicked', () => {
        const wrapper = createShallowEditor(null, 5);

        expect(wrapper.state('translation')).toEqual(TRANSLATION_PLURAL);
        wrapper.find('.action-copy').simulate('click');
        expect(wrapper.state('translation')).toEqual(SELECTED_ENTITY.original_plural);
    });

    it('calls the suggest action when the Suggest button is clicked', () => {
        const suggestMock = sinon.spy();
        const wrapper = createShallowEditor(suggestMock);

        wrapper.find('.action-send').simulate('click');
        expect(suggestMock.calledOnce).toBeTrue;
    });
});
