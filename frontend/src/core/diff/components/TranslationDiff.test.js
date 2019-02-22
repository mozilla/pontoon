import React from 'react';
import { shallow } from 'enzyme';

import TranslationDiff from './TranslationDiff';


describe('<TranslationDiff>', () => {
    it('returns the correct diff for provided strings', () => {
        const wrapper = shallow(
            <TranslationDiff
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
            <TranslationDiff
                base={ 'abcdef' }
                target={ 'abcdef' }
            />
        );

        expect(wrapper.find('ins')).toHaveLength(0);
        expect(wrapper.find('del')).toHaveLength(0);
        expect(wrapper.find('span')).toHaveLength(1);
    });
});
