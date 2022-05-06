import { shallow } from 'enzyme';
import React from 'react';
import sinon from 'sinon';

import * as Hooks from '~/hooks';
import * as Actions from '../actions';
import { BATCHACTIONS } from '../reducer';

import { ApproveAll } from './ApproveAll';
import { BatchActions } from './BatchActions';
import { RejectAll } from './RejectAll';
import { ReplaceAll } from './ReplaceAll';

const DEFAULT_BATCH_ACTIONS = {
  entities: [],
  lastCheckedEntity: null,
  requestInProgress: null,
  response: null,
};

describe('<BatchActions>', () => {
  beforeAll(() => {
    sinon.stub(Hooks, 'useAppDispatch').returns(() => {});
    sinon
      .stub(Hooks, 'useAppSelector')
      .callsFake((sel) => sel({ [BATCHACTIONS]: DEFAULT_BATCH_ACTIONS }));
    sinon.stub(Actions, 'resetSelection').returns({ type: 'whatever' });
    sinon.stub(Actions, 'selectAll').returns({ type: 'whatever' });
  });

  afterEach(() => {
    Actions.resetSelection.reset();
    Actions.selectAll.reset();
  });

  afterAll(() => {
    Hooks.useAppDispatch.restore();
    Hooks.useAppSelector.restore();
    Actions.resetSelection.restore();
    Actions.selectAll.restore();
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
    expect(Actions.resetSelection.called).toBeTruthy();
  });

  it('selects all entities when the Select All button is clicked', () => {
    const wrapper = shallow(<BatchActions />);

    wrapper.find('.select-all').simulate('click');
    expect(Actions.selectAll.called).toBeTruthy();
  });
});
