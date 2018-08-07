import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';

import * as editorActions from '../actions';

import Editor, { EditorBase } from './Editor';


const TRANSLATION = 'test';
const SELECTED_ENTITY = {
    pk: 42,
    original: 'le test',
    translation: [{string: TRANSLATION}],
};
const NAVIGATION = {
    entity: 42,
    locale: 'kg',
};


function createShallowEditor() {
    return shallow(<EditorBase
        activeTranslation={ TRANSLATION }
        navigation={ NAVIGATION }
        selectedEntity={ SELECTED_ENTITY }
    />);
}


describe('<EditorBase>', () => {
    it('renders correctly', () => {
        const wrapper = createShallowEditor();

        expect(wrapper.find('button')).toHaveLength(3);
        expect(wrapper.find('textarea').html()).toContain(TRANSLATION);
    });

    it('updates the textarea when the state changes', () => {
        const wrapper = createShallowEditor();

        expect(wrapper.find('textarea').html()).not.toContain('something else');
        wrapper.setState({translation: 'something else'});
        expect(wrapper.find('textarea').html()).toContain('something else');
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
});

describe('<Editor>', () => {
    const ENTITIES = [
        SELECTED_ENTITY,
        {
            pk: 1,
            original: 'something',
            translation: [{string: 'quelque chose'}],
        },
    ];

    beforeAll(() => {
        const suggestMock = sinon.stub(editorActions, 'suggest');
        suggestMock.returns({
            type: 'whatever',
        });
    });

    afterAll(() => {
        editorActions.suggest.release();
    });

    it('calls the suggest action when the Suggest button is clicked', () => {
        const initialState = {
            entities: {
                entities: ENTITIES
            },
            router: {
                location: {
                    pathname: '/kg/pro/all/',
                    search: '?string=42',
                },
            },
        };
        const store = createReduxStore(initialState);

        const wrapper = mount(<Editor
            store={ store }
        />);

        wrapper.find('.action-send').simulate('click');
        expect(editorActions.suggest.called).toEqual(true);
    });
});
