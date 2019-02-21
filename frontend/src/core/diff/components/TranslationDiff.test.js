import React from 'react';
import { shallow } from 'enzyme';

import { TranslationDiffBase } from './TranslationDiff';


describe('<TranslationDiffBase>', () => {
    it('returns the correct diff for provided strings', () => {
        const wrapper = shallow(
            <TranslationDiffBase
                base={ 'abcdef' }
                target={ 'cdefgh' }
            />
        );

        expect(wrapper.find('ins')).toHaveLength(1);
        expect(wrapper.find('del')).toHaveLength(1);
        expect(wrapper.find('span')).toHaveLength(1);
    });

    it('returns the same string if provided strings are equal', () => {
        const wrapper = shallow(
            <TranslationDiffBase
                base={ 'abcdef' }
                target={ 'abcdef' }
            />
        );

        expect(wrapper.find('ins')).toHaveLength(0);
        expect(wrapper.find('del')).toHaveLength(0);
        expect(wrapper.find('span')).toHaveLength(1);
    });
});
