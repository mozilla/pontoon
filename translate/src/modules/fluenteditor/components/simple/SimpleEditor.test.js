import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';
import sinon from 'sinon';

import { LocationProvider } from '~/context/location';
import * as editor from '~/core/editor';
import { RECEIVE_ENTITIES } from '~/core/entities/actions';
import { fluent } from '~/core/utils';

import { createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import SimpleEditor from './SimpleEditor';

const ENTITIES = [
  {
    pk: 1,
    original: 'my-message = Hello',
    translation: [
      {
        string: 'my-message = Salut',
      },
    ],
  },
];

function createSimpleEditor(entityIndex = 1) {
  const store = createReduxStore();

  const history = createMemoryHistory({
    initialEntries: ['/kg/firefox/all-resources/'],
  });

  const wrapper = mount(
    <Provider store={store}>
      <LocationProvider history={history}>
        <MockLocalizationProvider>
          <SimpleEditor ftlSwitch={null} />
        </MockLocalizationProvider>
      </LocationProvider>
    </Provider>,
  );

  store.dispatch({
    type: RECEIVE_ENTITIES,
    entities: ENTITIES,
    hasMore: false,
  });
  act(() => history.push(`?string=${entityIndex}`));

  wrapper.update();

  return [wrapper, store];
}

describe('<SimpleEditor>', () => {
  it('parses content that comes from an external source', () => {
    const [wrapper, store] = createSimpleEditor();

    // Update the content with a non-formatted Fluent string.
    store.dispatch(editor.actions.update('my-message = Coucou', 'external'));

    // Force a re-render -- see https://enzymejs.github.io/enzyme/docs/api/ReactWrapper/update.html
    wrapper.setProps({});

    // The translation has been updated to a simplified preview.
    expect(wrapper.find('textarea').text()).toEqual('Coucou');
  });

  it('does not render when translation is not a string', () => {
    const [wrapper, store] = createSimpleEditor();

    // Update the content with a non-formatted Fluent string.
    store.dispatch(
      editor.actions.update(fluent.parser.parseEntry('hello = World')),
    );
    wrapper.update();

    expect(wrapper.isEmptyRender()).toBeTruthy();
  });

  it('passes a reconstructed translation to sendTranslation', () => {
    const sendTranslationMock = sinon.stub(editor.actions, 'sendTranslation');
    sendTranslationMock.returns({ type: 'whatever' });

    const [wrapper, store] = createSimpleEditor();

    store.dispatch(editor.actions.update('Coucou'));
    wrapper.update();

    // Intercept the sendTranslation prop and call it directly.
    wrapper.find('GenericTranslationForm').prop('sendTranslation')();

    expect(sendTranslationMock.calledOnce).toBeTruthy();
    expect(sendTranslationMock.lastCall.args[1]).toEqual(
      'my-message = Coucou\n',
    );

    sendTranslationMock.restore();
  });
});
