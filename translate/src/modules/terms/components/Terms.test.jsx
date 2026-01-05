import { render } from '@testing-library/react';
import React from 'react';

import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { createReduxStore, MockStore } from '~/test/store';

import { Terms } from './Terms';
import { vi } from 'vitest';

const Wrap = ({ children }) => (
  <MockStore store={createReduxStore({ user: { isAuthenticated: true } })}>
    <Locale.Provider value={{ code: 'kg' }}>
      <EntityView.Provider value={{ entity: {} }}>
        <EditorActions.Provider value={{ setEditorSelection: () => {} }}>
          {children}
        </EditorActions.Provider>
      </EntityView.Provider>
    </Locale.Provider>
  </MockStore>
);

describe('<Terms>', () => {
  let getSelectionBackup;

  beforeAll(() => {
    getSelectionBackup = window.getSelection;
    window.getSelection = () => null;
    vi.mock('@fluent/react', async (importOriginal) => {
      const actual = await importOriginal();
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

  it('returns null while terms are loading', () => {
    const { container } = render(
      <Wrap>
        <Terms terms={{ fetching: true }} />
      </Wrap>,
    );
    expect(container.textContent).toBe('');
  });

  it('renders a no terms message when no terms are available', () => {
    const { container } = render(
      <Wrap>
        <Terms terms={{ terms: [] }} />
      </Wrap>,
    );
    expect(container.querySelectorAll('.no-terms')).toHaveLength(1);
  });

  it('renders terms list correctly', () => {
    const { container } = render(
      <Wrap>
        <Terms
          terms={{
            terms: [{ text: 'text1' }, { text: 'text2' }, { text: 'text3' }],
          }}
        />
      </Wrap>,
    );

    expect(container.querySelectorAll('.no-terms')).toHaveLength(0);
    expect(container.querySelectorAll('header')).toHaveLength(3);
  });
});
