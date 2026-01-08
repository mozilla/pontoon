import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';

import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { createReduxStore, MockStore } from '~/test/store';

import { Term } from './Term';
import { vi } from 'vitest';

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
    vi.mock('@fluent/react', async () => {
      const actual = await vi.importActual('@fluent/react');
      return {
        ...actual,
        Localized: ({ children }) => children,
      };
    });
  });

  afterAll(() => {
    window.getSelection = getSelectionBackup;
    vi.restoreAllMocks();
  });

  it('renders term correctly', () => {
    const { container } = render(
      <MockTerm isAuthenticated setEditorSelection={vi.fn()} />,
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
    const spy = vi.fn();
    const { container } = render(
      <MockTerm isAuthenticated setEditorSelection={spy} />,
    );
    await userEvent.click(container.querySelector('li'));
    expect(spy).toHaveBeenCalled();
  });

  it('does not call the addTextToEditorTranslation function if term not translated', async () => {
    const spy = vi.fn();
    const { container } = render(
      <MockTerm
        isAuthenticated
        setEditorSelection={spy}
        term={{ ...TERM, translation: '' }}
      />,
    );
    await userEvent.click(container.querySelector('li'));
    expect(spy).not.toHaveBeenCalled();
  });

  it('does not call the addTextToEditorTranslation function if read-only editor', async () => {
    const spy = vi.fn();
    const { container } = render(
      <MockTerm isAuthenticated={false} setEditorSelection={spy} />,
    );
    await userEvent.click(container.querySelector('li'));
    expect(spy).not.toHaveBeenCalled();
  });
});
