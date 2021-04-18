import React from 'react';
import { mount, shallow } from 'enzyme';

import Machinery from './Machinery';

describe('<Machinery>', () => {
    const LOCALE = {
        code: 'kg',
    };

    const ENTITY = {
        machinery_original: 'Plus ultra',
        format: 'po',
    };

    it('shows a search form', () => {
        const machinery = {
            translations: [],
            searchResults: [],
        };
        const wrapper = shallow(
            <Machinery machinery={machinery} locale={LOCALE} entity={ENTITY} />,
        );

        expect(wrapper.find('.search-wrapper')).toHaveLength(1);
        expect(
            wrapper.find('#machinery-Machinery--search-placeholder'),
        ).toHaveLength(1);
    });

    it('shows the correct number of translations', () => {
        const machinery = {
            translations: [
                { original: '1' },
                { original: '2' },
                { original: '3' },
            ],
            searchResults: [{ original: '4' }, { original: '5' }],
        };
        const wrapper = shallow(
            <Machinery machinery={machinery} locale={LOCALE} entity={ENTITY} />,
        );

        expect(wrapper.find('Translation')).toHaveLength(5);
    });

    it('returns null if there is no locale', () => {
        const machinery = {};
        const wrapper = shallow(
            <Machinery machinery={machinery} locale={null} entity={ENTITY} />,
        );

        expect(wrapper.type()).toBeNull();
    });

    it('renders a reset button if a source string is present', () => {
        const machinery = {
            translations: [],
            searchResults: [],
            sourceString: 'test',
        };
        const wrapper = mount(
            <Machinery machinery={machinery} locale={LOCALE} entity={ENTITY} />,
        );

        expect(wrapper.find('button')).toHaveLength(1);
    });
});
