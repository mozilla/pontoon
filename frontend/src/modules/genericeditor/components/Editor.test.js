import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { EditorBase } from './Editor';


const ENTITIES = [
    {
        pk: 1,
        translation: [{
            string: 'quelque chose',
        }],
    },
    {
        pk: 2,
        translation: [
            { string: 'test' },
        ],
    },
];


function createEditorBase() {
    const updateTranslationMock = sinon.stub();
    const wrapper = shallow(<EditorBase
        editor={ { translation: '' } }
        pluralForm={ -1 }
        entity={ ENTITIES[0] }
        activeTranslationString={ ENTITIES[0].translation[0].string }
        updateTranslation={ updateTranslationMock }
    />);

    return [wrapper, updateTranslationMock];
}


describe('<Editor>', () => {
    it('updates translation on mount', () => {
        const [, updateTranslationMock] = createEditorBase();
        expect(updateTranslationMock.calledOnce).toBeTruthy();
    });

    it('updates translation on component update', () => {
        const [wrapper, updateTranslationMock] = createEditorBase();
        expect(updateTranslationMock.calledOnce).toBeTruthy();

        wrapper.setProps({ entity: ENTITIES[1] });
        expect(updateTranslationMock.calledTwice).toBeTruthy();

        wrapper.setProps({ pluralForm: 1 });
        expect(updateTranslationMock.calledThrice).toBeTruthy();
    });
});
