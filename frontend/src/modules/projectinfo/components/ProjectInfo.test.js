import React from 'react';
import sinon from 'sinon';

import { createReduxStore } from 'test/store';
import { shallowUntilTarget } from 'test/utils';

import * as project from 'core/project';

import ProjectInfo, { ProjectInfoBase } from './ProjectInfo';


describe('<ProjectInfo>', () => {
    beforeAll(() => {
        sinon.stub(project.actions, 'get').returns({type: 'whatever'});
    });

    afterEach(() => {
        // Make sure tests do not pollute one another.
        project.actions.get.resetHistory();
    });

    afterAll(() => {
        project.actions.get.restore();
    });

    it('returns null when data is being fetched', () => {
        const store = createReduxStore();
        store.dispatch(project.actions.request());
        const wrapper = shallowUntilTarget(<ProjectInfo store={ store } />, ProjectInfoBase);

        expect(wrapper.type()).toBeNull();
    });

    it('returns null when name is null', () => {
        const store = createReduxStore();
        store.dispatch(project.actions.receive({ name: '', info: '' }));
        const wrapper = shallowUntilTarget(<ProjectInfo store={ store } />, ProjectInfoBase);

        expect(wrapper.type()).toBeNull();
    });

    it('returns null when project is all-projects', () => {
        const store = createReduxStore({
            router: {
                location: {
                    pathname: '/kg/all-projects/all-resources/',
                }
            },
        });
        store.dispatch(project.actions.receive({ name: 'All The Projects', info: '' }));
        const wrapper = shallowUntilTarget(<ProjectInfo store={ store } />, ProjectInfoBase);

        expect(wrapper.type()).toBeNull();
    });
});
