import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import ReplaceAll from './ReplaceAll';

const DEFAULT_BATCH_ACTIONS = {
    entities: [],
    lastCheckedEntity: null,
    requestInProgress: null,
    response: null,
};

describe('<ReplaceAll>', () => {
    it('renders default button correctly', () => {
        const wrapper = shallow(
            <ReplaceAll batchactions={DEFAULT_BATCH_ACTIONS} />,
        );

        expect(wrapper.find('.replace-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ReplaceAll--default')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-ReplaceAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-ReplaceAll--success')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ReplaceAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders error button correctly', () => {
        const wrapper = shallow(
            <ReplaceAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'replace',
                        error: true,
                    },
                }}
            />,
        );

        expect(wrapper.find('.replace-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ReplaceAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ReplaceAll--error')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ReplaceAll--success')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ReplaceAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders success button correctly', () => {
        const wrapper = shallow(
            <ReplaceAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'replace',
                        changedCount: 2,
                    },
                }}
            />,
        );

        expect(wrapper.find('.replace-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ReplaceAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ReplaceAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-ReplaceAll--success')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-ReplaceAll--invalid')).toHaveLength(
            0,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('renders success with invalid button correctly', () => {
        const wrapper = shallow(
            <ReplaceAll
                batchactions={{
                    ...DEFAULT_BATCH_ACTIONS,
                    response: {
                        action: 'replace',
                        changedCount: 2,
                        invalidCount: 1,
                    },
                }}
            />,
        );

        expect(wrapper.find('.replace-all')).toHaveLength(1);
        expect(wrapper.find('#batchactions-ReplaceAll--default')).toHaveLength(
            0,
        );
        expect(wrapper.find('#batchactions-ReplaceAll--error')).toHaveLength(0);
        expect(wrapper.find('#batchactions-ReplaceAll--success')).toHaveLength(
            1,
        );
        expect(wrapper.find('#batchactions-ReplaceAll--invalid')).toHaveLength(
            1,
        );
        expect(wrapper.find('.fa')).toHaveLength(0);
    });

    it('performs replace all action when Replace All button is clicked', () => {
        const mockReplaceAll = sinon.spy();

        const wrapper = shallow(
            <ReplaceAll
                batchactions={DEFAULT_BATCH_ACTIONS}
                replaceAll={mockReplaceAll}
            />,
        );

        expect(mockReplaceAll.called).toBeFalsy();
        wrapper.find('.replace-all').simulate('click');
        expect(mockReplaceAll.called).toBeTruthy();
    });
});
