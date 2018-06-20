import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import store from 'store';
import { shallowUntilTarget } from 'testUtils';

import * as actions from '../actions';
import Entity from './Entity';
import EntitiesList, { EntitiesListBase } from './EntitiesList';


describe('<EntitiesList>', () => {
    it('shows the correct number of entities', () => {
        const entities = [
            {
                original: 'a',
            },
            {
                original: 'b',
            },
        ]
        store.dispatch(actions.receive(entities));
        const wrapper = shallowUntilTarget(<EntitiesList store={ store } />, EntitiesListBase);
        expect(wrapper.find('Entity')).toHaveLength(2);
    });
});
