import React from 'react';
import { mount } from 'enzyme';

import { MachineryTranslations } from '~/context/MachineryTranslations';
import { SearchData } from '~/context/SearchData';
import { MockLocalizationProvider } from '~/test/utils';

import { Machinery } from './Machinery';

jest.mock('~/hooks', () => ({
  useAppDispatch: () => () => {},
  useAppSelector: () => {},
}));

const mountMachinery = (translations, search) =>
  mount(
    <MockLocalizationProvider>
      <MachineryTranslations.Provider
        value={{ source: 'source', translations }}
      >
        <SearchData.Provider
          value={{
            input: '',
            query: '',
            page: 1,
            fetching: false,
            results: [],
            hasMore: false,
            setInput: () => {},
            getResults: () => {},
            ...search,
          }}
        >
          <Machinery entity={{ pk: 42 }} />
        </SearchData.Provider>
      </MachineryTranslations.Provider>
    </MockLocalizationProvider>,
  );

describe('<Machinery>', () => {
  it('shows a search form', () => {
    const wrapper = mountMachinery([], {});

    expect(wrapper.find('.search-wrapper')).toHaveLength(1);
    expect(wrapper.find('#machinery-search')).toHaveLength(1);
  });

  it('shows the correct number of translations', () => {
    const wrapper = mountMachinery(
      [
        { original: '1', sources: [] },
        { original: '2', sources: [] },
        { original: '3', sources: [] },
      ],
      {
        results: [
          { original: '4', sources: [] },
          { original: '5', sources: [] },
        ],
      },
    );

    expect(wrapper.find('MachineryTranslationComponent')).toHaveLength(5);
  });

  it('renders a reset button if a search query is present', () => {
    const wrapper = mountMachinery([], { input: 'test', query: 'test' });

    expect(wrapper.find('button')).toHaveLength(1);
  });
});
