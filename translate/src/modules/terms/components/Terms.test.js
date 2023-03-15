import * as Fluent from '@fluent/react';
import { render } from '@testing-library/react';
import React from 'react';
import sinon from 'sinon';

import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { createReduxStore, MockStore } from '~/test/store';

import { Terms } from './Terms';

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
    sinon.stub(Fluent, 'Localized').callsFake(({ children }) => children);
  });

  afterAll(() => {
    window.getSelection = getSelectionBackup;
    Fluent.Localized.restore();
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
