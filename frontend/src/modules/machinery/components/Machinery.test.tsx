import React from 'react';
import { mount, shallow } from 'enzyme';

import Machinery from './Machinery';

describe('<Machinery>', () => {
    const LOCALE = {
        code: 'kg',
    };

    it('shows a search form', () => {
        const machinery = {
            translations: [],
        };
        const wrapper = shallow(
            <Machinery machinery={machinery} locale={LOCALE} />,
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
        };
        const wrapper = shallow(
            <Machinery machinery={machinery} locale={LOCALE} />,
        );

        expect(wrapper.find('Translation')).toHaveLength(3);
    });

    it('returns null if there is no locale', () => {
        const machinery = {};
        const wrapper = shallow(
            <Machinery machinery={machinery} locale={null} />,
        );

        expect(wrapper.type()).toBeNull();
    });

    it('renders a reset button if a source string is present', () => {
        const machinery = {
            translations: [],
            sourceString: 'test',
        };
        const wrapper = mount(
            <Machinery machinery={machinery} locale={LOCALE} />,
        );

        expect(wrapper.find('button')).toHaveLength(1);
    });
});
