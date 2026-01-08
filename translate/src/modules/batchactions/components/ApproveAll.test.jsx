import React from 'react';
import { mount } from 'enzyme';

import { MockLocalizationProvider } from '~/test/utils';

import { ApproveAll } from './ApproveAll';
import { vi } from 'vitest';

const DEFAULT_BATCH_ACTIONS = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

const WrapApproveAll = (props) => (
  <MockLocalizationProvider>
    <ApproveAll {...props} />
  </MockLocalizationProvider>
);

describe('<ApproveAll>', () => {
  it('renders default button correctly', () => {
    const wrapper = mount(
      <WrapApproveAll batchactions={DEFAULT_BATCH_ACTIONS} />,
    );

    expect(wrapper.find('.approve-all')).toHaveLength(1);
    expect(wrapper.find('#batchactions-ApproveAll--default')).toHaveLength(1);
    expect(wrapper.find('#batchactions-ApproveAll--error')).toHaveLength(0);
    expect(wrapper.find('#batchactions-ApproveAll--success')).toHaveLength(0);
    expect(wrapper.find('#batchactions-ApproveAll--invalid')).toHaveLength(0);
    expect(wrapper.find('.fas')).toHaveLength(0);
  });

  it('renders error button correctly', () => {
    const wrapper = mount(
      <WrapApproveAll
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
    expect(wrapper.find('#batchactions-ApproveAll--default')).toHaveLength(0);
    expect(wrapper.find('#batchactions-ApproveAll--error')).toHaveLength(1);
    expect(wrapper.find('#batchactions-ApproveAll--success')).toHaveLength(0);
    expect(wrapper.find('#batchactions-ApproveAll--invalid')).toHaveLength(0);
    expect(wrapper.find('.fas')).toHaveLength(0);
  });

  it('renders success button correctly', () => {
    const wrapper = mount(
      <WrapApproveAll
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
    expect(wrapper.find('#batchactions-ApproveAll--default')).toHaveLength(0);
    expect(wrapper.find('#batchactions-ApproveAll--error')).toHaveLength(0);
    expect(wrapper.find('#batchactions-ApproveAll--success')).toHaveLength(1);
    expect(wrapper.find('#batchactions-ApproveAll--invalid')).toHaveLength(0);
    expect(wrapper.find('.fas')).toHaveLength(0);
  });

  it('renders success with invalid button correctly', () => {
    const wrapper = mount(
      <WrapApproveAll
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
    expect(wrapper.find('#batchactions-ApproveAll--default')).toHaveLength(0);
    expect(wrapper.find('#batchactions-ApproveAll--error')).toHaveLength(0);
    expect(wrapper.find('#batchactions-ApproveAll--success')).toHaveLength(1);
    expect(wrapper.find('#batchactions-ApproveAll--invalid')).toHaveLength(1);
    expect(wrapper.find('.fas')).toHaveLength(0);
  });

  it('performs approve all action when Approve All button is clicked', () => {
    const mockApproveAll = vi.fn();

    const wrapper = mount(
      <WrapApproveAll
        batchactions={DEFAULT_BATCH_ACTIONS}
        approveAll={mockApproveAll}
      />,
    );

    expect(mockApproveAll).not.toHaveBeenCalled();
    wrapper.find('.approve-all').simulate('click');
    expect(mockApproveAll).toHaveBeenCalled();
  });
});
