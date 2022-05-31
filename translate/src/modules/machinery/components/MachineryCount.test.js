import React from 'react';
import { mount } from 'enzyme';

import { MachineryTranslations } from '~/context/MachineryTranslations';
import { SearchData } from '~/context/SearchData';

import { MachineryCount } from './MachineryCount';

const mountMachineryCount = (translations, results) =>
  mount(
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
    const wrapper = mountMachineryCount(
      [
        { sources: ['translation-memory'] },
        { sources: ['translation-memory'] },
      ],
      [],
    );

    // There are only preferred results.
    expect(wrapper.find('.count > span')).toHaveLength(1);

    // And there are two of them.
    expect(wrapper.find('.preferred').text()).toContain('2');

    expect(wrapper.text()).not.toContain('+');
  });

  it('shows the correct number of remaining translations', () => {
    const wrapper = mountMachineryCount(
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
    expect(wrapper.find('.count > span')).toHaveLength(1);
    expect(wrapper.find('.preferred')).toHaveLength(0);

    // And there are three of them.
    expect(wrapper.find('.count > span').text()).toContain('5');

    expect(wrapper.text()).not.toContain('+');
  });

  it('shows the correct numbers of preferred and remaining translations', () => {
    const wrapper = mountMachineryCount(
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
    expect(wrapper.find('.count > span')).toHaveLength(3);

    // And each count is correct.
    expect(wrapper.find('.preferred').text()).toContain('2');
    expect(wrapper.find('.count > span').last().text()).toContain('5');

    // And the final display is correct as well.
    expect(wrapper.text()).toEqual('2+5');
  });
});
