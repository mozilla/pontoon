import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import * as navigation from 'core/navigation';
import * as user from 'core/user';
import * as history from 'modules/history';

import { actions as entityActions } from '..';

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
    it('shows a message when no entity is selected', () => {
        const wrapper = createShallowEntityDetails(null);
        expect(wrapper.text()).toContain('Select an entity');
    });

    it('loads the correct list of components', () => {
        const wrapper = createShallowEntityDetails();

        expect(wrapper.text()).toContain('Metadata');
        expect(wrapper.text()).toContain('Editor');
    });
});

describe('<EntityDetails>', () => {
    beforeAll(() => {
        const suggestMock = sinon.stub(entityActions, 'sendTranslation');
        suggestMock.returns({
            type: 'whatever',
        });
        const updateMock = sinon.stub(history.actions, 'updateStatus');
        updateMock.returns({
            type: 'whatever',
        });
        const saveSettingMock = sinon.stub(user.actions, 'saveSetting');
        saveSettingMock.returns({
            type: 'whatever',
        });
    });

    afterAll(() => {
        entityActions.sendTranslation.restore();
        history.actions.updateStatus.restore();
        user.actions.saveSetting.restore();
    });

    it('dispatches the updateStatus action when updateTranslationStatus is called', () => {
        const [wrapper] = createEntityDetailsWithStore();

        wrapper.instance().updateTranslationStatus(42, 'fake translation');
        expect(history.actions.updateStatus.calledOnce).toBeTruthy();
    });

    it('dispatches the saveSetting action when updateSetting is called', () => {
        const [wrapper] = createEntityDetailsWithStore();

        wrapper.instance().updateSetting('setting', true);
        expect(user.actions.saveSetting.calledOnce).toBeTruthy();
        expect(
            user.actions.saveSetting
            .calledWith('setting', true, USER.username)
        ).toBeTruthy();
    });

    it('calls the sendTranslation action when the sendTranslation method is ran', () => {
        const [wrapper] = createEntityDetailsWithStore();

        wrapper.instance().sendTranslation('fake translation');
        expect(entityActions.sendTranslation.calledOnce).toBeTruthy();
        expect(
            entityActions.sendTranslation
            .calledWith(ENTITIES[0].pk, 'fake translation', 'kg', ENTITIES[0].original)
        ).toBeTruthy();
    });

    it('updates translation state when props change', () => {
        const [wrapper, store] = createEntityDetailsWithStore();

        expect(wrapper.state('translation')).toEqual(TRANSLATION);

        // This doesn't work yet, see https://github.com/airbnb/enzyme/issues/2009
        // store.dispatch(navigation.actions.updateEntity(store.getState().router, ENTITIES[1].pk));
        // wrapper.update();
        // expect(wrapper.state('translation')).toEqual(ENTITIES[1].translation[0].string);
    });
});
