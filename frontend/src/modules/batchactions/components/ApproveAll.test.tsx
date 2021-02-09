import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import ApproveAll from './ApproveAll';

const DEFAULT_BATCH_ACTIONS = {
    entities: [],
    lastCheckedEntity: null,
    requestInProgress: null,
    response: null,
};

describe('<ApproveAll>', () => {
    it('renders default button correctly', () => {
        const wrapper = shallow(
            <ApproveAll batchactions={DEFAULT_BATCH_ACTIONS} />,
        );

        expect(wrapper.find('.approve-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ApproveAll--default')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-ApproveAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-ApproveAll--success')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ApproveAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders error button correctly', () => {
        const wrapper = shallow(
            <ApproveAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'approve',
                        error: true,
                    },
                }}
            />,
        );

        expect(wrapper.find('.approve-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ApproveAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ApproveAll--error')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ApproveAll--success')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ApproveAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders success button correctly', () => {
        const wrapper = shallow(
            <ApproveAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'approve',
                        changedCount: 2,
                    },
                }}
            />,
        );

        expect(wrapper.find('.approve-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ApproveAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ApproveAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-ApproveAll--success')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-ApproveAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders success with invalid button correctly', () => {
        const wrapper = shallow(
            <ApproveAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'approve',
                        changedCount: 2,
                        invalidCount: 1,
                    },
                }}
            />,
        );

        expect(wrapper.find('.approve-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ApproveAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ApproveAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-ApproveAll--success')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-ApproveAll--invalid')).toHaveLength(
            1,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('performs approve all action when Approve All button is clicked', () => {
        const mockApproveAll = sinon.spy();

        const wrapper = shallow(
            <ApproveAll
                batchactions={DEFAULT_BATCH_ACTIONS}
                approveAll={mockApproveAll}
            />,
        );

        expect(mockApproveAll.called).toBeFalsy();
        wrapper.find('.approve-all').simulate('click');
        expect(mockApproveAll.called).toBeTruthy();
    });
});
