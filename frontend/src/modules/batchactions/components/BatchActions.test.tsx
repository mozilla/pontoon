import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { BatchActionsBase } from './BatchActions';

import ApproveAll from './ApproveAll';
import RejectAll from './RejectAll';
import ReplaceAll from './ReplaceAll';

import { actions } from '..';

const DEFAULT_BATCH_ACTIONS = {
    entities: [],
    lastCheckedEntity: null,
    requestInProgress: null,
    response: null,
};

describe('<BatchActionsBase>', () => {
    beforeAll(() => {
        sinon.stub(actions, 'resetSelection').returns({ type: 'whatever' });
        sinon.stub(actions, 'selectAll').returns({ type: 'whatever' });
    });

    afterEach(() => {
        actions.resetSelection.reset();
        actions.selectAll.reset();
    });

    afterAll(() => {
        actions.resetSelection.restore();
        actions.selectAll.restore();
    });

    it('renders correctly', () => {
        const wrapper = shallow(
            <BatchActionsBase batchactions={DEFAULT_BATCH_ACTIONS} />,
        );

        expect(wrapper.find('.batch-actions')).toHaveLength(1);

        expect(wrapper.find('.topbar')).toHaveLength(1);
        expect(wrapper.find('.selected-count')).toHaveLength(1);
        expect(wrapper.find('.select-all')).toHaveLength(1);

        expect(wrapper.find('.main-content')).toHaveLength(1);

        expect(
            wrapper.find('#batchactions-BatchActions--warning'),
        ).toHaveLength(1);

        expect(
            wrapper.find('#batchactions-BatchActions--review-heading'),
        ).toHaveLength(1);
        expect(wrapper.find(ApproveAll)).toHaveLength(1);
        expect(wrapper.find(RejectAll)).toHaveLength(1);

        expect(
            wrapper.find('#batchactions-BatchActions--find-replace-heading'),
        ).toHaveLength(1);
        expect(wrapper.find('#batchactions-BatchActions--find')).toHaveLength(
            1,
        );
        expect(
            wrapper.find('#batchactions-BatchActions--replace-with'),
        ).toHaveLength(1);
        expect(wrapper.find(ReplaceAll)).toHaveLength(1);
    });

    it('closes batch actions panel when the Close button with selected count is clicked', () => {
        const wrapper = shallow(
            <BatchActionsBase
                batchactions={DEFAULT_BATCH_ACTIONS}
                dispatch={() => {}}
            />,
        );

        wrapper.find('.selected-count').simulate('click');
        expect(actions.resetSelection.called).toBeTruthy();
    });

    it('selects all entities when the Select All button is clicked', () => {
        const wrapper = shallow(
            <BatchActionsBase
                batchactions={DEFAULT_BATCH_ACTIONS}
                dispatch={() => {}}
                parameters={{}}
            />,
        );

        wrapper.find('.select-all').simulate('click');
        expect(actions.selectAll.called).toBeTruthy();
    });
});
