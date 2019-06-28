import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { EditorBase } from './Editor';


const ENTITIES = [
    {
        pk: 1,
        original: 'my-message = Hello',
        translation: [{
            string: 'my-message = Salut',
        }],
    },
    {
        pk: 2,
        original: 'my-message = Hello\n    .my-attr = World!',
        translation: [
            { string: 'my-message = Salut\n    .my-attr = Monde !' },
        ],
    },
    {
        pk: 3,
        original: 'my-message =\n    .my-attr = Something guud',
        translation: [
            { string: 'my-message =\n    .my-attr = Quelque chose de bien' },
        ],
    },
];


function createEditorBase({
    entityIndex = 0,
} = {}) {
    const updateTranslationMock = sinon.stub();
    const wrapper = shallow(<EditorBase
        activeTranslation={ ENTITIES[entityIndex].translation[0].string }
        entity={ ENTITIES[entityIndex] }
        pluralForm={ -1 }
        translation={ ENTITIES[entityIndex].translation[0].string }
        setInitialTranslation={ sinon.stub() }
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
    });

    it('renders the simple form when passing a simple string', () => {
        const [wrapper, ] = createEditorBase();

        expect(wrapper.find('SourceEditor').exists()).toBeFalsy();
        expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();
    });

    it('renders the simple form when passing a simple string with one attribute', () => {
        const [wrapper, ] = createEditorBase({
            entityIndex: 2,
        });
        
        expect(wrapper.find('SourceEditor').exists()).toBeFalsy();
        expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();
    });

    it('renders the source form when passing a complex string', () => {
        const [wrapper, ] = createEditorBase({
            entityIndex: 1,
        });

        expect(wrapper.find('SourceEditor').exists()).toBeTruthy();
        expect(wrapper.find('SimpleEditor').exists()).toBeFalsy();
    });

    it('converts translation when switching source mode', () => {
        const [wrapper, updateTranslationMock] = createEditorBase();
        expect(wrapper.find('SimpleEditor').exists()).toBeTruthy();
        expect(updateTranslationMock.calledWith('Salut')).toBeTruthy();

        // We've mocked the `updateTranslation` method so it's never called.
        // Simulate here what it would do.
        wrapper.setProps({ editor: { translation: 'Salut' } });

        // Force source mode.
        wrapper.instance().toggleForceSource();

        expect(wrapper.find('SourceEditor').exists()).toBeTruthy();
        expect(updateTranslationMock.lastCall.calledWith('my-message = Salut')).toBeTruthy();
    });
});
