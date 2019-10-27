import React from 'react';
import { shallow } from 'enzyme';

import TranslationSource from './TranslationSource';


const DEFAULT_TRANSLATION = {
    sources: [
        {
            type: 'translation-memory',
            url: 'http://pontoon.mozilla.org',
        },
    ]
};


describe('<TranslationSource>', () => {
    [{id: 'translation-memory', component: 'TranslationMemory'},
        {id: 'google-translate', component: 'GoogleTranslation'},
        {id: 'microsoft-translator', component: 'MicrosoftTranslation'},
        {id: 'microsoft-terminology', component: 'MicrosoftTerminology'},
        {id: 'transvision', component: 'TransvisionMemory'},
        {id: 'caighdean', component: 'CaighdeanTranslation'},
    ].forEach(({id, component}) =>
        it(`renders ${component} component for ${id} type correctly`, () => {
            const translation = {
                sources: [
                    {
                        type: id,
                    },
                ],
            };
            const wrapper = shallow(<TranslationSource
                translation={ translation }
            />);

            expect(wrapper.find(component)).toHaveLength(1);
        }))

    it('shows several sources', () => {
        const translation = {
            sources: [
                ...DEFAULT_TRANSLATION.sources,
                {
                    type: 'microsoft-terminology',
                    url: 'https://www.microsoft.com/Language/en-US/Search.aspx?sString=',
                },
            ],
        };
        const wrapper = shallow(<TranslationSource
            translation={ translation }
        />);

        expect(wrapper.find('TranslationMemory')).toHaveLength(1);
        expect(wrapper.find('MicrosoftTerminology')).toHaveLength(1);
    });
});
