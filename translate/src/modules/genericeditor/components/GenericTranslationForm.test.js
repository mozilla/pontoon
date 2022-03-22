import sinon from 'sinon';

import { update as updateEditor, updateSelection } from '~/core/editor/actions';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import GenericTranslationForm from './GenericTranslationForm';

function createComponent(updateTranslation) {
  const store = createReduxStore();
  store.dispatch(updateEditor('Hello'));

  const wrapper = mountComponentWithStore(GenericTranslationForm, store, {
    updateTranslation,
  });

  return [wrapper, store];
}

describe('<GenericTranslationForm>', () => {
  it('renders a textarea with some content', () => {
    const [wrapper] = createComponent();

    expect(wrapper.find('textarea')).toHaveLength(1);
    expect(wrapper.find('textarea').html()).toContain('Hello');
  });

  it('calls the updateTranslation function on change', () => {
    const updateMock = sinon.spy();
    const [wrapper] = createComponent(updateMock);

    expect(updateMock.called).toBeFalsy();
    wrapper
      .find('textarea')
      .simulate('change', { currentTarget: { value: 'good bye' } });
    expect(updateMock.called).toBeTruthy();
  });

  it('updates the translation when selectionReplacementContent is passed', async () => {
    const updateMock = sinon.spy();
    const [wrapper, store] = createComponent(updateMock);

    await store.dispatch(updateSelection('World, '));

    // Force a re-render -- see https://enzymejs.github.io/enzyme/docs/api/ReactWrapper/update.html
    wrapper.setProps({});

    expect(updateMock.calledOnce).toBeTruthy();
    expect(updateMock.calledWith('World, Hello')).toBeTruthy();
  });
});
