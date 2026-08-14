import React from 'react';
import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { EditorData, EditorResult } from '~/context/Editor';
import { MockLocalizationProvider } from '~/test/utils';

import { MachinerySourceIndicator } from './MachinerySourceIndicator';

const entry = (value) => ({ format: 'plain', id: 'key', value: [value] });

const mount = ({ autofilled = entry('Bonjour'), result = entry('Bonjour') }) =>
  render(
    <MockLocalizationProvider
      resources={[
        `editor-MachinerySourceIndicator--match = <stress>100%</stress> MATCH
    .title = 100% Translation Memory match`,
      ]}
    >
      <EditorData.Provider value={{ autofilled, sourceView: false }}>
        <EditorResult.Provider value={result}>
          <MachinerySourceIndicator />
        </EditorResult.Provider>
      </EditorData.Provider>
    </MockLocalizationProvider>,
  );

describe('<MachinerySourceIndicator>', () => {
  it('shows for content that was filled in automatically', () => {
    const { container } = mount({});

    const indicator = container.querySelector('.tm-source');
    expect(indicator).not.toBeNull();
    expect(indicator.textContent).toContain('100%');
    expect(indicator.getAttribute('title')).toBeTruthy();
  });

  it('shows for a multi-field entry filled in from a composed match', () => {
    const composed = {
      format: 'fluent',
      id: 'key',
      value: ['Valeur'],
      attributes: new Map([['label', ['Étiquette']]]),
    };
    const { container } = mount({ autofilled: composed, result: composed });

    expect(container.querySelector('.tm-source')).not.toBeNull();
  });

  it('shows nothing when nothing was filled in', () => {
    const { container } = mount({ autofilled: null });

    expect(container.querySelector('.tm-source')).toBeNull();
  });

  it('shows nothing once the filled-in content has been edited', () => {
    const { container } = mount({ result: entry('Bonjour !') });

    expect(container.querySelector('.tm-source')).toBeNull();
  });
});
