import React from 'react';
import { shallow } from 'enzyme';

import Translation from './Translation';


describe('<Translation>', () => {
    const DEFAULT_TRANSLATION = {
        sources: [
            {
                type: 'Translation memory',
                url: 'http://pontoon.mozilla.org',
                title: 'Pontoon',
            },
        ],
        original: 'A horse, a horse! My kingdom for a horse!',
        translation: 'Un cheval, un cheval ! Mon royaume pour un cheval !',
    };

    const DEFAULT_LOCALE = {
        direction: 'ltr',
        code: 'kg',
        script: 'Latin',
    };

    it('renders a translation correctly', () => {
        const wrapper = shallow(<Translation
            translation={ DEFAULT_TRANSLATION }
            locale={ DEFAULT_LOCALE }
        />);

        expect(wrapper.find('.original').text()).toContain('A horse, a horse!');
        expect(wrapper.find('.suggestion').text()).toContain('Un cheval, un cheval !');

        expect(wrapper.find('ul li')).toHaveLength(1);
        expect(wrapper.find('ul li a').text()).toEqual('Translation memory');

        // No count.
        expect(wrapper.find('ul li sup')).toHaveLength(0);
        // No quality.
        expect(wrapper.find('.stress')).toHaveLength(0);
    });

    it('shows quality when possible', () => {
        const translation = {
            ...DEFAULT_TRANSLATION,
            quality: 100,
        };
        const wrapper = shallow(<Translation
            translation={ translation }
            locale={ DEFAULT_LOCALE }
        />);

        expect(wrapper.find('.stress')).toHaveLength(1);
        expect(wrapper.find('.stress').text()).toEqual('100%');
    });

    it('shows several sources', () => {
        const translation = {
            ...DEFAULT_TRANSLATION,
            sources: [
                ...DEFAULT_TRANSLATION.sources,
                {
                    type: 'Transvision',
                    url: '',
                    title: 'Transvision memory',
                    count: 24,
                },
            ],
        };
        const wrapper = shallow(<Translation
            translation={ translation }
            locale={ DEFAULT_LOCALE }
        />);

        expect(wrapper.find('ul').text()).toContain('Translation memory');
        expect(wrapper.find('ul').text()).toContain('Transvision');

        expect(wrapper.find('ul li sup')).toHaveLength(1);
        expect(wrapper.find('ul li sup').text()).toEqual('24');
    });
});
