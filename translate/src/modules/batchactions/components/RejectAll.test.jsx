import { mount } from 'enzyme';
import React from 'react';

import { MockLocalizationProvider } from '~/test/utils';

import { RejectAll } from './RejectAll';
import { vi } from 'vitest';

const DEFAULT_BATCH_ACTIONS = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

const WrapRejectAll = (props) => (
  <MockLocalizationProvider>
    <RejectAll {...props} />
  </MockLocalizationProvider>
);

describe('<RejectAll>', () => {
  it('renders default button correctly', () => {
    const wrapper = mount(
      <WrapRejectAll batchactions={DEFAULT_BATCH_ACTIONS} />,
    );

    expect(wrapper.find('.reject-all')).toHaveLength(1);
    expect(wrapper.find('#batchactions-RejectAll--default')).toHaveLength(1);
    expect(wrapper.find('#batchactions-RejectAll--error')).toHaveLength(0);
    expect(wrapper.find('#batchactions-RejectAll--success')).toHaveLength(0);
    expect(wrapper.find('#batchactions-RejectAll--invalid')).toHaveLength(0);
    expect(wrapper.find('.fas')).toHaveLength(0);
  });

  it('renders error button correctly', () => {
    const wrapper = mount(
      <WrapRejectAll
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
    expect(wrapper.find('#batchactions-RejectAll--default')).toHaveLength(0);
    expect(wrapper.find('#batchactions-RejectAll--error')).toHaveLength(1);
    expect(wrapper.find('#batchactions-RejectAll--success')).toHaveLength(0);
    expect(wrapper.find('#batchactions-RejectAll--invalid')).toHaveLength(0);
    expect(wrapper.find('.fas')).toHaveLength(0);
  });

  it('renders success button correctly', () => {
    const wrapper = mount(
      <WrapRejectAll
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
    expect(wrapper.find('#batchactions-RejectAll--default')).toHaveLength(0);
    expect(wrapper.find('#batchactions-RejectAll--error')).toHaveLength(0);
    expect(wrapper.find('#batchactions-RejectAll--success')).toHaveLength(1);
    expect(wrapper.find('#batchactions-RejectAll--invalid')).toHaveLength(0);
    expect(wrapper.find('.fas')).toHaveLength(0);
  });

  it('renders success with invalid button correctly', () => {
    const wrapper = mount(
      <WrapRejectAll
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
    expect(wrapper.find('#batchactions-RejectAll--default')).toHaveLength(0);
    expect(wrapper.find('#batchactions-RejectAll--error')).toHaveLength(0);
    expect(wrapper.find('#batchactions-RejectAll--success')).toHaveLength(1);
    expect(wrapper.find('#batchactions-RejectAll--invalid')).toHaveLength(1);
    expect(wrapper.find('.fas')).toHaveLength(0);
  });

  it('raise confirmation warning when Reject All button is clicked', () => {
    const mockRejectAll = vi.fn();

    const wrapper = mount(
      <WrapRejectAll
        batchactions={DEFAULT_BATCH_ACTIONS}
        rejectAll={mockRejectAll}
      />,
    );

    expect(mockRejectAll).not.toHaveBeenCalled();
    wrapper.find('.reject-all').simulate('click');
    expect(mockRejectAll).not.toHaveBeenCalled();
    expect(wrapper.find('#batchactions-RejectAll--confirmation')).toHaveLength(
      1,
    );
  });

  it('performs reject all action when Reject All button is confirmed', () => {
    const mockRejectAll = vi.fn();

    const wrapper = mount(
      <WrapRejectAll
        batchactions={DEFAULT_BATCH_ACTIONS}
        rejectAll={mockRejectAll}
      />,
    );

    expect(mockRejectAll).not.toHaveBeenCalled();
    wrapper.find('.reject-all').simulate('click');
    wrapper.find('.reject-all').simulate('click');
    expect(mockRejectAll).toHaveBeenCalled();
  });
});
