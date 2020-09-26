import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { EditorBase } from './Editor';

const ENTITIES = [
    {
        pk: 1,
        translation: [
            {
                string: 'quelque chose',
            },
        ],
    },
    {
        pk: 2,
        translation: [{ string: 'test' }],
    },
];

function createEditorBase() {
    const setInitialTranslationMock = sinon.stub();
    const updateTranslationMock = sinon.stub();
    const wrapper = shallow(
        <EditorBase
            editor={{ translation: '' }}
            pluralForm={-1}
            entity={ENTITIES[0]}
            activeTranslationString={ENTITIES[0].translation[0].string}
            setInitialTranslation={setInitialTranslationMock}
            updateTranslation={updateTranslationMock}
        />,
    );

    return [wrapper, setInitialTranslationMock, updateTranslationMock];
}

describe('<Editor>', () => {
    it('updates translation on mount', () => {
        const [, , updateTranslationMock] = createEditorBase();
        expect(updateTranslationMock.calledOnce).toBeTruthy();
    });

    it('sets initial translation on mount', () => {
        const [, setInitialTranslationMock] = createEditorBase();
        expect(setInitialTranslationMock.calledOnce).toBeTruthy();
    });

    it('updates translation when entity or plural change', () => {
        const [wrapper, updateTranslationMock] = createEditorBase();
        expect(updateTranslationMock.calledOnce).toBeTruthy();

        wrapper.setProps({ entity: ENTITIES[1] });
        expect(updateTranslationMock.calledTwice).toBeTruthy();

        wrapper.setProps({ pluralForm: 1 });
        expect(updateTranslationMock.calledThrice).toBeTruthy();
    });

    it('sets initial translation when entity or plural change', () => {
        const [wrapper, setInitialTranslationMock] = createEditorBase();
        expect(setInitialTranslationMock.calledOnce).toBeTruthy();

        wrapper.setProps({ entity: ENTITIES[1] });
        expect(setInitialTranslationMock.calledTwice).toBeTruthy();

        wrapper.setProps({ pluralForm: 1 });
        expect(setInitialTranslationMock.calledThrice).toBeTruthy();
    });

    it('does not update translation when translation changes', () => {
        const [wrapper, updateTranslationMock] = createEditorBase();
        expect(updateTranslationMock.calledOnce).toBeTruthy();

        wrapper.setProps({ editor: { translation: 'hello' } });
        expect(updateTranslationMock.calledOnce).toBeTruthy();
    });

    it('does not set initial translation when translation changes', () => {
        const [wrapper, setInitialTranslationMock] = createEditorBase();
        expect(setInitialTranslationMock.calledOnce).toBeTruthy();

        wrapper.setProps({ editor: { translation: 'hello' } });
        expect(setInitialTranslationMock.calledOnce).toBeTruthy();
    });
});
