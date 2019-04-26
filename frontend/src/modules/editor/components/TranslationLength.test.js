import React from 'react';
import { shallow } from 'enzyme';

import TranslationLengthBase from './TranslationLength';


describe('<TranslationLengthBase>', () => {
    const LENGTH_ENTITY = {
        comment: '',
        original: '12345',
    };

    const COUNTDOWN_ENTITY = {
        comment: 'MAX_LENGTH: 5',
        format: 'lang',
        original: '12345',
    };

    it('shows translation length and original string length', () => {
        const wrapper = shallow(<TranslationLengthBase
            translation='1234567'
            entity={ LENGTH_ENTITY }
        />);

        expect(wrapper.find('.countdown')).toHaveLength(0);
        expect(wrapper.find('.translation-vs-original').childAt(0).text()).toEqual('7');
        expect(wrapper.find('.translation-vs-original').childAt(1).text()).toEqual('|');
        expect(wrapper.find('.translation-vs-original').childAt(2).text()).toEqual('5');
    });

    it('shows countdown if MAX_LENGTH provided in LANG entity comment', () => {
        const wrapper = shallow(<TranslationLengthBase
            translation='123'
            entity={ COUNTDOWN_ENTITY }
        />);

        expect(wrapper.find('.translation-vs-original')).toHaveLength(0);
        expect(wrapper.find('.countdown span').text()).toEqual('2');
        expect(wrapper.find('.countdown span.overflow')).toHaveLength(0);
    });

    it('marks countdown overflow', () => {
        const wrapper = shallow(<TranslationLengthBase
            translation='123456'
            entity={ COUNTDOWN_ENTITY }
        />);

        expect(wrapper.find('.countdown span.overflow')).toHaveLength(1);
    });

    it('strips html from translation when calculating countdown', () => {
        const wrapper = shallow(<TranslationLengthBase
            translation='12<span>34</span>56'
            entity={ COUNTDOWN_ENTITY }
        />);

        expect(wrapper.find('.countdown span').text()).toEqual('-1');
    });

    it('does not strips html from translation when calculating length', () => {
        const wrapper = shallow(<TranslationLengthBase
            translation='12<span>34</span>56'
            entity={ LENGTH_ENTITY }
        />);

        expect(wrapper.find('.translation-vs-original').childAt(0).text()).toEqual('19');
    });
});
