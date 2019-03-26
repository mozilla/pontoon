import React from 'react';
import { shallow } from 'enzyme';

import Translation from './Translation';


describe('<Translation>', () => {
    const ORIGINAL = 'A horse, a horse! My kingdom for a horse!';
    const DEFAULT_TRANSLATION = {
        sources: [
            {
                type: 'Translation memory',
                url: 'http://pontoon.mozilla.org',
                title: 'Pontoon',
            },
        ],
        original: ORIGINAL,
        translation: 'Un cheval, un cheval ! Mon royaume pour un cheval !',
    };

    const DEFAULT_LOCALE = {
        direction: 'ltr',
        code: 'kg',
        script: 'Latin',
    };

    const DEFAULT_ENTITY = {
        original: ORIGINAL,
    };

    it('renders a translation correctly', () => {
        const wrapper = shallow(<Translation
            translation={ DEFAULT_TRANSLATION }
            locale={ DEFAULT_LOCALE }
            entity={ DEFAULT_ENTITY }
        />);

        expect(wrapper.find('.original').find('WithDiff')).toHaveLength(1);
        expect(wrapper.find('.suggestion').find('ContentMarker').props().children).toContain('Un cheval, un cheval !');

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
            entity={ DEFAULT_ENTITY }
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
            entity={ DEFAULT_ENTITY }
        />);

        expect(wrapper.find('ul').text()).toContain('Translation memory');
        expect(wrapper.find('ul').text()).toContain('Transvision');

        expect(wrapper.find('ul li sup')).toHaveLength(1);
        expect(wrapper.find('ul li sup').text()).toEqual('24');
    });
});
