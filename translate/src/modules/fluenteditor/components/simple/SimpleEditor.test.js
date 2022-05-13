/* eslint-env node */

import { mount } from 'enzyme';
import { createMemoryHistory } from 'history';
import React from 'react';
import { act } from 'react-dom/test-utils';
import { Provider } from 'react-redux';
import sinon from 'sinon';

import { LocationProvider } from '~/context/Location';
import * as SendTranslation from '~/core/editor/hooks/useSendTranslation';
import { updateTranslation } from '~/core/editor/actions';
import { RECEIVE_ENTITIES } from '~/core/entities/actions';
import { parser } from '~/core/utils/fluent';

import { createReduxStore } from '~/test/store';
import { MockLocalizationProvider } from '~/test/utils';

import { SimpleEditor } from './SimpleEditor';

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
    store.dispatch(updateTranslation('my-message = Coucou', 'external'));

    // Force a re-render -- see https://enzymejs.github.io/enzyme/docs/api/ReactWrapper/update.html
    wrapper.setProps({});

    // The translation has been updated to a simplified preview.
    expect(wrapper.find('textarea').text()).toEqual('Coucou');
  });

  it('does not render when translation is not a string', () => {
    const [wrapper, store] = createSimpleEditor();

    // Update the content with a non-formatted Fluent string.
    store.dispatch(updateTranslation(parser.parseEntry('hello = World')));
    wrapper.update();

    expect(wrapper.isEmptyRender()).toBeTruthy();
  });

  it('passes a reconstructed translation to sendTranslation', () => {
    const sendTranslationMock = sinon.stub().returns({ type: 'whatever' });
    sinon
      .stub(SendTranslation, 'useSendTranslation')
      .returns(sendTranslationMock);

    try {
      const [wrapper, store] = createSimpleEditor();

      store.dispatch(updateTranslation('Coucou'));
      wrapper.update();

      // Intercept the sendTranslation prop and call it directly.
      wrapper.find('GenericTranslationForm').prop('sendTranslation')();

      expect(sendTranslationMock.getCalls()).toMatchObject([
        { args: [undefined, 'my-message = Coucou\n'] },
      ]);
    } finally {
      SendTranslation.useSendTranslation.restore();
    }
  });
});
