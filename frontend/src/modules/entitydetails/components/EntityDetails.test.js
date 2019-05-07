import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

// import * as navigation from 'core/navigation';
import * as editor from 'modules/editor';
import * as history from 'modules/history';

import EntityDetails, { EntityDetailsBase } from './EntityDetails';


const ENTITIES = [
    {
        pk: 42,
        original: 'le test',
        translation: [{string: 'test'}],
    },
    {
        pk: 1,
        original: 'something',
        translation: [{string: 'quelque chose'}],
    },
];
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
const PARAMETERS = {
    pluralForm: 0,
};
const HISTORY = {
    translations: [],
};
const LOCALES = {
    translations: [],
};
const USER = {
    settings: {
        forceSuggestions: true,
    },
    username: 'Franck',
}


function createShallowEntityDetails(selectedEntity = SELECTED_ENTITY) {
    return shallow(<EntityDetailsBase
        activeTranslation={ TRANSLATION }
        history={ HISTORY }
        otherlocales={ LOCALES }
        navigation={ NAVIGATION }
        selectedEntity={ selectedEntity }
        parameters={ PARAMETERS }
        locale={ { code: 'kg' } }
        dispatch={ () => {} }
        user={ { settings: {} } }
    />);
}


function createEntityDetailsWithStore() {
    const initialState = {
        entities: {
            entities: ENTITIES
        },
        user: USER,
        router: {
            location: {
                pathname: '/kg/pro/all/',
                search: '?string=' + ENTITIES[0].pk,
            },
        },
        locales: {
            locales: {
                'kg': {
                    code: 'kg',
                },
            },
        },
    };
    const store = createReduxStore(initialState);

    return [shallowUntilTarget(
        <EntityDetails store={ store } />,
        EntityDetailsBase
    ), store];
}


describe('<EntityDetailsBase>', () => {
    beforeAll(() => {
        sinon.stub(editor.actions, 'updateFailedChecks').returns({ type: 'whatever'});
        sinon.stub(editor.actions, 'resetFailedChecks').returns({ type: 'whatever'});
    });

    afterEach(() => {
        editor.actions.updateFailedChecks.reset();
        editor.actions.resetFailedChecks.reset();
    });

    afterAll(() => {
        editor.actions.updateFailedChecks.restore();
        editor.actions.resetFailedChecks.restore();
    });

    it('shows an empty section when no entity is selected', () => {
        const wrapper = createShallowEntityDetails(null);
        expect(wrapper.text()).toContain('');
    });

    it('loads the correct list of components', () => {
        const wrapper = createShallowEntityDetails();

        expect(wrapper.text()).toContain('EntityNavigation');
        expect(wrapper.text()).toContain('Metadata');
        expect(wrapper.text()).toContain('Editor');
        expect(wrapper.text()).toContain('Helpers');
    });

    it('shows failed checks for approved (or fuzzy) translations with errors or warnings', () => {
        const wrapper = createShallowEntityDetails();

        wrapper.setProps({
            pluralForm: -1,
            selectedEntity: {
                pk: 2,
                original: 'something',
                translation: [{
                    approved: true,
                    string: 'quelque chose',
                    errors: ['Error1'],
                    warnings: ['Warning1'],
                }],
            },
        });

        expect(editor.actions.updateFailedChecks.calledOnce).toBeTruthy();
        expect(editor.actions.resetFailedChecks.calledOnce).toBeFalsy();
    });

    it('hides failed checks for approved (or fuzzy) translations without errors or warnings', () => {
        const wrapper = createShallowEntityDetails();

        wrapper.setProps({
            pluralForm: -1,
            selectedEntity: {
                pk: 2,
                original: 'something',
                translation: [{
                    approved: true,
                    string: 'quelque chose',
                    errors: [],
                    warnings: [],
                }],
            },
        });

        expect(editor.actions.updateFailedChecks.calledOnce).toBeFalsy();
        expect(editor.actions.resetFailedChecks.calledOnce).toBeTruthy();
    });
});

describe('<EntityDetails>', () => {
    beforeAll(() => {
        // sinon.stub(editor.actions, 'update').returns({ type: 'whatever'});
        sinon.stub(history.actions, 'updateStatus').returns({ type: 'whatever'});
    });

    afterAll(() => {
        // editor.actions.update.restore();
        history.actions.updateStatus.restore();
    });

    it('dispatches the updateStatus action when updateTranslationStatus is called', () => {
        const [wrapper] = createEntityDetailsWithStore();

        wrapper.instance().updateTranslationStatus(42, 'fake translation');
        expect(history.actions.updateStatus.calledOnce).toBeTruthy();
    });

    // This doesn't work yet, see https://github.com/airbnb/enzyme/issues/2009
    // it('updates translation state when props change', () => {
    //     const [ wrapper, store ] = createEntityDetailsWithStore();
    //
    //     store.dispatch(navigation.actions.updateEntity(store.getState().router, ENTITIES[1].pk));
    //     wrapper.update();
    //     expect(editor.update.calledOnce).toBeTruthy();
    // });
});
