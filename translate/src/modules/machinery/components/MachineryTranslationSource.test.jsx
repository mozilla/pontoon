import React from 'react';

import { MachineryTranslationSource } from './MachineryTranslationSource';
import { render } from '@testing-library/react';

vi.mock('~/hooks', () => ({
  useAppSelector: (selector) =>
    selector({
      term: { terms: [], fetching: false, entity: 0, locale: '' },
      teamcomments: { comments: [], fetching: false, entity: null },
    }),
}));

import { MockLocalizationProvider } from '~/test/utils';

const DEFAULT_TRANSLATION = {
  sources: ['translation-memory'],
};
const WrapMachineryTranslationSource = (props) => {
  return (
    <MockLocalizationProvider>
      <MachineryTranslationSource {...props} />
    </MockLocalizationProvider>
  );
};
const translationMemoryTitle = 'TRANSLATION MEMORY';
const googleTranslationTitle = 'GOOGLE TRANSLATE';
const microsoftTranslationTitle = 'MICROSOFT TRANSLATOR';
const microsoftTerminologyTitle = 'MICROSOFT';
const caighdeanTranslationTitle = 'CAIGHDEAN';

describe('<MachineryTranslationSource>', () => {
  for (const [type, component, title] of [
    ['translation-memory', 'TranslationMemory', translationMemoryTitle],
    ['google-translate', 'GoogleTranslation', googleTranslationTitle],
    ['microsoft-translator', 'MicrosoftTranslation', microsoftTranslationTitle],
    [
      'microsoft-terminology',
      'MicrosoftTerminology',
      microsoftTerminologyTitle,
    ],
    ['caighdean', 'CaighdeanTranslation', caighdeanTranslationTitle],
  ]) {
    it(`renders ${type} type for ${component} component correctly`, () => {
      const translation = {
        sources: [type],
      };
      const { getByText } = render(
        <WrapMachineryTranslationSource translation={translation} />,
      );

      getByText(title);
    });
  }

  it('shows several sources', () => {
    const translation = {
      sources: [...DEFAULT_TRANSLATION.sources, 'microsoft-terminology'],
    };
    const { getByText } = render(
      <WrapMachineryTranslationSource translation={translation} />,
    );

    getByText(translationMemoryTitle);
    getByText(microsoftTerminologyTitle);
  });

  it('leads with Translation Memory, which the quality score belongs to', () => {
    // Google Translate resolving first used to render
    // `100% • GOOGLE TRANSLATE • TRANSLATION MEMORY`, reading as if the score
    // scored Google Translate.
    const { container } = render(
      <WrapMachineryTranslationSource
        translation={{
          sources: ['google-translate', 'translation-memory'],
          quality: 100,
        }}
      />,
    );

    const sources = container.querySelector('ul.sources');
    expect(sources.firstElementChild).toHaveTextContent(translationMemoryTitle);
  });

  it('keeps the order the other sources arrived in', () => {
    const { container } = render(
      <WrapMachineryTranslationSource
        translation={{
          sources: ['caighdean', 'microsoft-translator'],
        }}
      />,
    );

    const sources = container.querySelector('ul.sources');
    expect([...sources.children].map((li) => li.textContent)).toEqual([
      caighdeanTranslationTitle,
      microsoftTranslationTitle,
    ]);
  });

  describe('AI badge', () => {
    let root;

    beforeEach(() => {
      root = document.createElement('div');
      root.id = 'root';
      root.dataset.isOpenaiChatgptSupported = 'true';
      document.body.appendChild(root);
    });

    afterEach(() => root.remove());

    const sourceList = (translation, props) =>
      render(
        <WrapMachineryTranslationSource translation={translation} {...props} />,
      ).container.querySelector('ul.sources');

    it('comes last, not where its source landed in the list', () => {
      // Google Translate arriving anywhere but last used to leave the dropdown
      // stranded mid-list, because it hung off the label.
      const sources = sourceList({
        sources: ['google-translate', 'microsoft-translator'],
      });

      expect([...sources.children].map((li) => li.className)).toEqual([
        'google-translation',
        '',
        'ai-refine',
      ]);
    });

    it('carries no source label of its own', () => {
      const sources = sourceList({ sources: ['google-translate'] });
      const badge = sources.querySelector('li.ai-refine');

      expect(
        badge.querySelector('.translation-source'),
      ).not.toBeInTheDocument();
      expect(sources.querySelector('li.google-translation')).toHaveTextContent(
        googleTranslationTitle,
      );
    });

    it('is offered only for Google Translate output', () => {
      for (const source of [
        'translation-memory',
        'microsoft-translator',
        'caighdean',
      ]) {
        const sources = sourceList({ sources: [source] });
        expect(sources.querySelector('li.ai-refine')).not.toBeInTheDocument();
      }
    });

    it('is hidden when OpenAI is not supported', () => {
      root.dataset.isOpenaiChatgptSupported = 'false';
      const sources = sourceList({ sources: ['google-translate'] });

      expect(sources.querySelector('li.ai-refine')).not.toBeInTheDocument();
    });
  });
});
