import React from 'react';
import { shallow } from 'enzyme';

import TranslationLength from './TranslationLength';

describe('<TranslationLength>', () => {
    const LENGTH_ENTITY = {
        comment: '',
        original: '12345',
        original_plural: '123456',
    };

    const COUNTDOWN_ENTITY = {
        comment: 'MAX_LENGTH: 5\nThis is an actual comment.',
        format: 'lang',
        original: '12345',
    };

    it('shows translation length and original string length', () => {
        const wrapper = shallow(
            <TranslationLength
                comment={LENGTH_ENTITY.comment}
                format={LENGTH_ENTITY.format}
                original={LENGTH_ENTITY.original}
                translation='1234567'
            />,
        );

        expect(wrapper.find('.countdown')).toHaveLength(0);
        expect(
            wrapper.find('.translation-vs-original').childAt(0).text(),
        ).toEqual('7');
        expect(
            wrapper.find('.translation-vs-original').childAt(1).text(),
        ).toEqual('|');
        expect(
            wrapper.find('.translation-vs-original').childAt(2).text(),
        ).toEqual('5');
    });

    it('shows translation length and plural original string length', () => {
        const wrapper = shallow(
            <TranslationLength
                comment={LENGTH_ENTITY.comment}
                format={LENGTH_ENTITY.format}
                original={LENGTH_ENTITY.original_plural}
                translation='1234567'
            />,
        );

        expect(
            wrapper.find('.translation-vs-original').childAt(2).text(),
        ).toEqual('6');
    });

    it('shows countdown if MAX_LENGTH provided in LANG entity comment', () => {
        const wrapper = shallow(
            <TranslationLength
                comment={COUNTDOWN_ENTITY.comment}
                format={COUNTDOWN_ENTITY.format}
                original={COUNTDOWN_ENTITY.original}
                translation='123'
            />,
        );

        expect(wrapper.find('.translation-vs-original')).toHaveLength(0);
        expect(wrapper.find('.countdown span').text()).toEqual('2');
        expect(wrapper.find('.countdown span.overflow')).toHaveLength(0);
    });

    it('marks countdown overflow', () => {
        const wrapper = shallow(
            <TranslationLength
                comment={COUNTDOWN_ENTITY.comment}
                format={COUNTDOWN_ENTITY.format}
                original={COUNTDOWN_ENTITY.original}
                translation='123456'
            />,
        );

        expect(wrapper.find('.countdown span.overflow')).toHaveLength(1);
    });

    it('strips html from translation when calculating countdown', () => {
        const wrapper = shallow(
            <TranslationLength
                comment={COUNTDOWN_ENTITY.comment}
                format={COUNTDOWN_ENTITY.format}
                original={COUNTDOWN_ENTITY.original}
                translation='12<span>34</span>56'
            />,
        );

        expect(wrapper.find('.countdown span').text()).toEqual('-1');
    });

    it('does not strips html from translation when calculating length', () => {
        const wrapper = shallow(
            <TranslationLength
                comment={LENGTH_ENTITY.comment}
                format={LENGTH_ENTITY.format}
                original={LENGTH_ENTITY.original}
                translation='12<span>34</span>56'
            />,
        );

        expect(
            wrapper.find('.translation-vs-original').childAt(0).text(),
        ).toEqual('19');
    });
});
