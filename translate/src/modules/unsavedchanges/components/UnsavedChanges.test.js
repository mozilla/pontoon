import * as ReactRedux from 'react-redux';
import sinon from 'sinon';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import * as actions from '../actions';

import { UnsavedChanges } from './UnsavedChanges';

describe('<UnsavedChanges>', () => {
  beforeAll(() => {
    sinon.stub(ReactRedux, 'useDispatch').returns(() => {});
    sinon.stub(actions, 'hideUnsavedChanges').returns({ type: 'whatever' });
    sinon.stub(actions, 'ignoreUnsavedChanges').returns({ type: 'whatever' });
  });

  afterEach(() => {
    actions.hideUnsavedChanges.reset();
    actions.ignoreUnsavedChanges.reset();
  });

  afterAll(() => {
    ReactRedux.useDispatch.restore();
    actions.hideUnsavedChanges.restore();
    actions.ignoreUnsavedChanges.restore();
  });

  it('renders correctly if shown', () => {
    const store = createReduxStore({ unsavedchanges: { shown: true } });
    const wrapper = mountComponentWithStore(UnsavedChanges, store);

    expect(wrapper.find('.unsaved-changes')).toHaveLength(1);
    expect(wrapper.find('.close')).toHaveLength(1);
    expect(wrapper.find('.title')).toHaveLength(1);
    expect(wrapper.find('.body')).toHaveLength(1);
    expect(wrapper.find('.proceed.anyway')).toHaveLength(1);
  });

  it('does not render if not shown', () => {
    const store = createReduxStore({ unsavedchanges: { shown: false } });
    const wrapper = mountComponentWithStore(UnsavedChanges, store);

    expect(wrapper.find('.unsaved-changes')).toHaveLength(0);
  });

  it('closes the unsaved changes popup when the Close button is clicked', () => {
    const store = createReduxStore({ unsavedchanges: { shown: true } });
    const wrapper = mountComponentWithStore(UnsavedChanges, store);

    wrapper.find('.close').simulate('click');
    expect(actions.hideUnsavedChanges.calledOnce).toBeTruthy();
  });

  it('ignores the unsaved changes popup when the Proceed button is clicked', () => {
    const store = createReduxStore({ unsavedchanges: { shown: true } });
    const wrapper = mountComponentWithStore(UnsavedChanges, store);

    wrapper.find('.proceed.anyway').simulate('click');
    expect(actions.ignoreUnsavedChanges.calledOnce).toBeTruthy();
  });
});
