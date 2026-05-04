import React from 'react';

import { MachineryTranslations } from '~/context/MachineryTranslations';
import { SearchData } from '~/context/SearchData';

import { MachineryCount } from './MachineryCount';
import { render } from '@testing-library/react';
import { expect } from 'vitest';

const mountMachineryCount = (translations, results) =>
  render(
    <MachineryTranslations.Provider value={{ source: 'source', translations }}>
      <SearchData.Provider
        value={{
          input: '',
          query: '',
          page: 1,
          fetching: false,
          results,
          hasMore: false,
          setInput: () => {},
          getResults: () => {},
        }}
      >
        <MachineryCount />
      </SearchData.Provider>
    </MachineryTranslations.Provider>,
  );

describe('<MachineryCount>', () => {
  it('shows the correct number of preferred translations', () => {
    const { container } = mountMachineryCount(
      [
        { sources: ['translation-memory'] },
        { sources: ['translation-memory'] },
      ],
      [],
    );

    // There are only preferred results.
    expect(container.querySelectorAll('.count > span')).toHaveLength(1);

    // And there are two of them.
    expect(container.querySelector('.preferred')).toHaveTextContent('2');

    expect(container).not.toHaveTextContent('+');
  });

  it('shows the correct number of remaining translations', () => {
    const { container } = mountMachineryCount(
      [
        { sources: ['microsoft'] },
        { sources: ['google'] },
        { sources: ['google'] },
      ],
      [
        { sources: ['concordance-search'] },
        { sources: ['concordance-search'] },
      ],
    );

    // There are only remaining results.
    expect(container.querySelectorAll('.count > span')).toHaveLength(1);
    expect(container.querySelector('.preferred')).toBeNull();

    // And there are three of them.
    expect(container.querySelector('.count > span')).toHaveTextContent('5');

    expect(container).not.toHaveTextContent('+');
  });

  it('shows the correct numbers of preferred and remaining translations', () => {
    const { container } = mountMachineryCount(
      [
        { sources: ['translation-memory'] },
        { sources: ['translation-memory'] },
        { sources: ['microsoft'] },
        { sources: ['google'] },
        { sources: ['google'] },
      ],
      [
        { sources: ['concordance-search'] },
        { sources: ['concordance-search'] },
      ],
    );

    // There are both preferred and remaining, and the '+' sign.
    expect(container.querySelectorAll('.count > span')).toHaveLength(3);

    // And each count is correct.
    expect(container.querySelector('.preferred')).toHaveTextContent('2');
    const spans = container.querySelectorAll('.count > span');
    expect(spans[spans.length - 1]).toHaveTextContent('5');

    // And the final display is correct as well.
    expect(container).toHaveTextContent('2+5');
  });
});
