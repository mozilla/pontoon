import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { SearchPanel, SearchPanelDialog } from './SearchPanel';
import { SEARCH_OPTIONS } from '../constants';

describe('<SearchPanelDialog>', () => {
  it('correctly sets search option as selected', () => {
    const selectedSearchOptions = {
      search_identifiers: false,
      search_exclude_source_strings: false,
      search_rejected_translations: true,
      search_match_case: true,
      search_match_whole_word: false,
    };

    const store = createReduxStore();
    const wrapper = mountComponentWithStore(SearchPanelDialog, store, {
      options: selectedSearchOptions,
      selectedSearchOptions,
    });

    for (let option of SEARCH_OPTIONS) {
      expect(wrapper.find(`.menu .${option.slug}`).hasClass('enabled')).toBe(
        selectedSearchOptions[option.slug],
      );
    }
  });

  for (let { slug } of SEARCH_OPTIONS) {
    describe(`option: ${slug}`, () => {
      it('toggles a search option on click on the option icon', () => {
        const onToggleOption = sinon.spy();
        const store = createReduxStore();
        const options = {
          search_identifiers: false,
          search_exclude_source_strings: false,
          search_rejected_translations: true,
          search_match_case: true,
          search_match_whole_word: false,
        };

        const wrapper = mountComponentWithStore(SearchPanelDialog, store, {
          selectedSearchOptions: options,
          onApplyOptions: sinon.spy(),
          onToggleOption,
          onDiscard: sinon.spy(),
        });

        wrapper.find(`.menu .${slug}`).simulate('click');

        expect(onToggleOption.calledWith(slug)).toBeTruthy();
      });
    });
  }

  it('applies selected options on click on the Apply button', () => {
    const onApplyOptions = sinon.spy();
    const options = {
      search_identifiers: false,
      search_exclude_source_strings: false,
      search_rejected_translations: true,
      search_match_case: true,
      search_match_whole_word: false,
    };
    const store = createReduxStore();
    const wrapper = mountComponentWithStore(SearchPanelDialog, store, {
      selectedSearchOptions: options,
      onApplyOptions,
    });

    wrapper.find('.search-button').simulate('click');

    expect(onApplyOptions.called).toBeTruthy();
  });
});

describe('<SearchPanel>', () => {
  it('shows a panel with options on click', () => {
    const options = {
      search_identifiers: false,
      search_exclude_source_strings: false,
      search_rejected_translations: true,
      search_match_case: true,
      search_match_whole_word: false,
    };
    const wrapper = shallow(<SearchPanel options={options} />);

    expect(wrapper.find('SearchPanelDialog')).toHaveLength(0);
    wrapper.find('.visibility-switch').simulate('click');
    expect(wrapper.find('SearchPanelDialog')).toHaveLength(1);
  });
});
