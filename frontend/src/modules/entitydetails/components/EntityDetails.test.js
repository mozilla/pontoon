import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import { actions as entityActions } from '..';

import EntityDetails, { EntityDetailsBase } from './EntityDetails';


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

    beforeAll(() => {
        const suggestMock = sinon.stub(entityActions, 'sendTranslation');
        suggestMock.returns({
            type: 'whatever',
        });
    });

    afterAll(() => {
        entityActions.sendTranslation.restore();
    });

    it('calls the sendTranslation action when the sendTranslation method is ran', () => {
        const initialState = {
            entities: {
                entities: ENTITIES
            },
            user: {
                settings: {
                    forceSuggestions: true,
                },
            },
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

        const wrapper = shallowUntilTarget(
            <EntityDetails store={ store } />,
            EntityDetailsBase
        );

        wrapper.instance().sendTranslation('fake translation');
        expect(entityActions.sendTranslation.calledOnce).toBeTruthy();
        expect(
            entityActions.sendTranslation
            .calledWith(ENTITIES[0].pk, 'fake translation', 'kg', ENTITIES[0].original)
        ).toBeTruthy();
    });
});
