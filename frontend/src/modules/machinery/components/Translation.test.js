import React from 'react';
import { shallow } from 'enzyme';

import Translation from './Translation';


describe('<Translation>', () => {
    const ORIGINAL = 'A horse, a horse! My kingdom for a horse!';
    const DEFAULT_TRANSLATION = {
        sources: [
            {
                type: {
                    string: 'Translation Memory',
                    id: 'api--translation-memory',
                },
                url: 'http://pontoon.mozilla.org',
                title: {
                    string: 'Pontoon Homepage',
                    id: 'api--pontoon-homepage',
                },
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

        expect(wrapper.find('.original').find('GenericTranslation')).toHaveLength(1);
        expect(
            wrapper.find('.suggestion').find('GenericTranslation').props().content
        ).toContain('Un cheval, un cheval !');

        // expect(wrapper.find('ul li')).toHaveLength(1);
        // expect(wrapper.find('ul li a Localized').props().id).toEqual('api--translation-memory');

        // No count.
        expect(wrapper.find('ul li sup')).toHaveLength(0);
        // No quality.
        expect(wrapper.find('.quality')).toHaveLength(0);
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

        expect(wrapper.find('.quality')).toHaveLength(1);
        expect(wrapper.find('.quality').text()).toEqual('100%');
    });

    it('shows several sources', () => {
        const translation = {
            ...DEFAULT_TRANSLATION,
            sources: [
                ...DEFAULT_TRANSLATION.sources,
                {
                    type: {
                        string: 'Transvision',
                    },
                    url: '',
                    title: {
                        string: 'Transvision Memory',
                        id: 'api--transvision-memory',
                    },
                    count: 24,
                },
            ],
        };
        const wrapper = shallow(<Translation
            translation={ translation }
            locale={ DEFAULT_LOCALE }
            entity={ DEFAULT_ENTITY }
        />);

        // expect(wrapper.find('ul li a Localized').at(0).props().id).toEqual('api--translation-memory');
        // expect(wrapper.find('ul li a span').children().text()).toEqual('Transvision');

        // expect(wrapper.find('ul li sup')).toHaveLength(1);
        // expect(wrapper.find('ul li sup').text()).toEqual('24');
    });
});
