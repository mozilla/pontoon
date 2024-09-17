import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { createReduxStore, mountComponentWithStore } from '~/test/store';

import { SearchPanel, SearchPanelDialog } from './SearchPanel';
import { SEARCH_OPTIONS } from '../constants';

describe('<SearchPanelDialog>', () => {
    it('correctly sets search option as selected', () => {
        const options = ['search_rejected_translations'];

        const store = createReduxStore();
        const wrapper = mountComponentWithStore(SearchPanelDialog, store, {
            options: { search_identifiers,
                search_translations_only,
                search_rejected_translations,
                search_match_case,
                search_match_whole_word, },
          });
    
        // for (let option of SEARCH_OPTIONS){
        //     expect(wrapper.find(`.menu .${option.slug}`.hasClass(`selected`)).toBe(
        //         option
        //     ))
        // }

        // for (let {slug} of SEARCH_OPTIONS){
        //     describe(`option: ${slug}`, () => {
        //         const onApplyOption = sinon.spy();
        //         const store = createReduxStore();
        //         const wrapper = mountComponentWithStore(SearchPanelDialog, store, {
        //             options: { search_identifiers,
        //                 search_translations_only: [slug],
        //                 search_rejected_translations,
        //                 search_match_case,
        //                 search_match_whole_word, },
        //         });
        //     })
        // }
    
    })
})