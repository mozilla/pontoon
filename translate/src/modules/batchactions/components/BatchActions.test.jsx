import { shallow } from 'enzyme';
import React from 'react';

import * as Hooks from '~/hooks';
import * as Actions from '../actions';
import { BATCHACTIONS } from '../reducer';

import { ApproveAll } from './ApproveAll';
import { BatchActions } from './BatchActions';
import { RejectAll } from './RejectAll';
import { ReplaceAll } from './ReplaceAll';
import { vi } from 'vitest';

const DEFAULT_BATCH_ACTIONS = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

describe('<BatchActions>', () => {
  beforeAll(() => {
    vi.mock('~/hooks', () => ({
      useAppDispatch: vi.fn(() => vi.fn()),
      useAppSelector: vi.fn((selector) =>
        selector({ [BATCHACTIONS]: DEFAULT_BATCH_ACTIONS }),
      ),
    }));

    vi.mock('../actions', () => ({
      resetSelection: vi.fn(() => ({ type: 'whatever' })),
      selectAll: vi.fn(() => ({ type: 'whatever' })),
    }));
  });

  afterAll(() => {
    Hooks.useAppDispatch.mockRestore();
    Hooks.useAppSelector.mockRestore();
    Actions.resetSelection.mockRestore();
    Actions.selectAll.mockRestore();
  });

  it('renders correctly', () => {
    const wrapper = shallow(<BatchActions />);

    expect(wrapper.find('.batch-actions')).toHaveLength(1);

    expect(wrapper.find('.topbar')).toHaveLength(1);
    expect(wrapper.find('.selected-count')).toHaveLength(1);
    expect(wrapper.find('.select-all')).toHaveLength(1);

    expect(wrapper.find('.actions-panel')).toHaveLength(1);

    expect(wrapper.find('#batchactions-BatchActions--warning')).toHaveLength(1);

    expect(
      wrapper.find('#batchactions-BatchActions--review-heading'),
    ).toHaveLength(1);
    expect(wrapper.find(ApproveAll)).toHaveLength(1);
    expect(wrapper.find(RejectAll)).toHaveLength(1);

    expect(
      wrapper.find('#batchactions-BatchActions--find-replace-heading'),
    ).toHaveLength(1);
    expect(wrapper.find('#batchactions-BatchActions--find')).toHaveLength(1);
    expect(
      wrapper.find('#batchactions-BatchActions--replace-with'),
    ).toHaveLength(1);
    expect(wrapper.find(ReplaceAll)).toHaveLength(1);
  });

  it('closes batch actions panel when the Close button with selected count is clicked', () => {
    const wrapper = shallow(<BatchActions />);

    wrapper.find('.selected-count').simulate('click');
    expect(Actions.resetSelection).toHaveBeenCalled();
  });

  it('selects all entities when the Select All button is clicked', () => {
    const wrapper = shallow(<BatchActions />);

    wrapper.find('.select-all').simulate('click');
    expect(Actions.selectAll).toHaveBeenCalled();
  });
});
