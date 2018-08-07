import React from 'react';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import * as actions from '../actions';
import EntitiesList, { EntitiesListBase } from './EntitiesList';


describe('<EntitiesList>', () => {
    it('shows the correct number of entities', () => {
        const store = createReduxStore();

        const entities = [
            {
                original: 'a',
            },
            {
                original: 'b',
            },
        ];
        store.dispatch(actions.receive(entities));
        const wrapper = shallowUntilTarget(<EntitiesList store={ store } />, EntitiesListBase);
        expect(wrapper.find('Entity')).toHaveLength(2);
    });
});
