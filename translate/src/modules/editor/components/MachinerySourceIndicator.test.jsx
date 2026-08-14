import React from 'react';
import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { EditorData } from '~/context/Editor';
import { MockLocalizationProvider } from '~/test/utils';

import { MachinerySourceIndicator } from './MachinerySourceIndicator';

const field = (value) => ({
  id: '',
  name: '',
  keys: [],
  labels: [],
  handle: { current: { value } },
});

const mount = (editor) =>
  render(
    <MockLocalizationProvider
      resources={[
        `editor-MachinerySourceIndicator--match = <stress>100%</stress> MATCH
    .title = 100% Translation Memory match`,
      ]}
    >
      <EditorData.Provider
        value={{
          fields: [field('Bonjour')],
          machinery: { manual: false, sources: [], translation: 'Bonjour' },
          sourceView: false,
          ...editor,
        }}
      >
        <MachinerySourceIndicator />
      </EditorData.Provider>
    </MockLocalizationProvider>,
  );

describe('<MachinerySourceIndicator>', () => {
  it('shows for content that was filled in automatically', () => {
    const { container } = mount();

    const indicator = container.querySelector('.tm-source');
    expect(indicator).not.toBeNull();
    expect(indicator.textContent).toContain('100%');
    // The badge is too small for the whole sentence, so it goes in the tooltip
    expect(indicator.getAttribute('title')).toBe(
      '100% Translation Memory match',
    );
  });

  it('shows nothing for a manual copy', () => {
    const { container } = mount({
      machinery: { manual: true, sources: [], translation: 'Bonjour' },
    });

    expect(container.querySelector('.tm-source')).toBeNull();
  });

  it('shows nothing once the filled-in content has been edited', () => {
    const { container } = mount({ fields: [field('Bonjour !')] });

    expect(container.querySelector('.tm-source')).toBeNull();
  });
});
