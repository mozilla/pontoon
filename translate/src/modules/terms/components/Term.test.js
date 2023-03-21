import * as Fluent from '@fluent/react';
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import sinon from 'sinon';

import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { createReduxStore, MockStore } from '~/test/store';

import { Term } from './Term';

const TERM = {
  text: 'text',
  partOfSpeech: 'partOfSpeech',
  definition: 'definition',
  usage: 'usage',
  translation: 'translation',
};

function MockTerm({ isAuthenticated, setEditorSelection, term }) {
  const store = createReduxStore({ user: { isAuthenticated } });
  return (
    <MockStore store={store}>
      <Locale.Provider value={{ code: 'kg' }}>
        <EntityView.Provider value={{ entity: {} }}>
          <EditorActions.Provider value={{ setEditorSelection }}>
            <Term term={term ?? TERM} />
          </EditorActions.Provider>
        </EntityView.Provider>
      </Locale.Provider>
    </MockStore>
  );
}

describe('<Term>', () => {
  let getSelectionBackup;

  beforeAll(() => {
    getSelectionBackup = window.getSelection;
    window.getSelection = () => null;
    sinon.stub(Fluent, 'Localized').callsFake(({ children }) => children);
  });

  afterAll(() => {
    window.getSelection = getSelectionBackup;
    Fluent.Localized.restore();
  });

  it('renders term correctly', () => {
    const { container } = render(
      <MockTerm isAuthenticated setEditorSelection={sinon.spy()} />,
    );

    expect(container.querySelectorAll('li')).toHaveLength(1);
    expect(container.querySelector('.text').textContent).toEqual('text');
    expect(container.querySelector('.part-of-speech').textContent).toEqual(
      'partOfSpeech',
    );
    expect(container.querySelector('.definition').textContent).toEqual(
      'definition',
    );
    expect(container.querySelector('.usage .content').textContent).toEqual(
      'usage',
    );
    expect(container.querySelector('.translation').textContent).toEqual(
      'translation',
    );
  });

  it('calls the addTextToEditorTranslation function on click', async () => {
    const spy = sinon.spy();
    const { container } = render(
      <MockTerm isAuthenticated setEditorSelection={spy} />,
    );
    await userEvent.click(container.querySelector('li'));
    expect(spy.called).toEqual(true);
  });

  it('does not call the addTextToEditorTranslation function if term not translated', async () => {
    const spy = sinon.spy();
    const { container } = render(
      <MockTerm
        isAuthenticated
        setEditorSelection={spy}
        term={{ ...TERM, translation: '' }}
      />,
    );
    await userEvent.click(container.querySelector('li'));
    expect(spy.called).toEqual(false);
  });

  it('does not call the addTextToEditorTranslation function if read-only editor', async () => {
    const spy = sinon.spy();
    const { container } = render(
      <MockTerm isAuthenticated={false} setEditorSelection={spy} />,
    );
    await userEvent.click(container.querySelector('li'));
    expect(spy.called).toEqual(false);
  });
});
