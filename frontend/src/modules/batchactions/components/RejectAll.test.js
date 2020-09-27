import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import RejectAll from './RejectAll';

const DEFAULT_BATCH_ACTIONS = {
    entities: [],
    lastCheckedEntity: null,
    requestInProgress: null,
    response: null,
};

describe('<RejectAll>', () => {
    it('renders default button correctly', () => {
        const wrapper = shallow(
            <RejectAll batchactions={DEFAULT_BATCH_ACTIONS} />,
        );

        expect(wrapper.find('.reject-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-RejectAll--default')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-RejectAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-RejectAll--success')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-RejectAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders error button correctly', () => {
        const wrapper = shallow(
            <RejectAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'reject',
                        error: true,
                    },
                }}
            />,
        );

        expect(wrapper.find('.reject-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-RejectAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-RejectAll--error')).toHaveLength(1);
        expect(wrapper.find('#batchactions-RejectAll--success')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-RejectAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders success button correctly', () => {
        const wrapper = shallow(
            <RejectAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'reject',
                        changedCount: 2,
                    },
                }}
            />,
        );

        expect(wrapper.find('.reject-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-RejectAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-RejectAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-RejectAll--success')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-RejectAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders success with invalid button correctly', () => {
        const wrapper = shallow(
            <RejectAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'reject',
                        changedCount: 2,
                        invalidCount: 1,
                    },
                }}
            />,
        );

        expect(wrapper.find('.reject-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-RejectAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-RejectAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-RejectAll--success')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-RejectAll--invalid')).toHaveLength(
            1,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('raise confirmation warning when Reject All button is clicked', () => {
        const mockRejectAll = sinon.spy();

        const wrapper = shallow(
            <RejectAll
                batchactions={DEFAULT_BATCH_ACTIONS}
                rejectAll={mockRejectAll}
            />,
        );

        expect(mockRejectAll.called).toBeFalsy();
        wrapper.find('.reject-all').simulate('click');
        expect(mockRejectAll.called).toBeFalsy();
        expect(
            wrapper.find('#batchactions-RejectAll--confirmation'),
        ).toHaveLength(1);
    });

    it('performs reject all action when Reject All button is confirmed', () => {
        const mockRejectAll = sinon.spy();

        const wrapper = shallow(
            <RejectAll
                batchactions={DEFAULT_BATCH_ACTIONS}
                rejectAll={mockRejectAll}
            />,
        );

        wrapper.instance().setState({ isConfirmationVisible: true });

        expect(mockRejectAll.called).toBeFalsy();
        wrapper.find('.reject-all').simulate('click');
        expect(mockRejectAll.called).toBeTruthy();
    });
});
