import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import Term from './Term';

describe('<Term>', () => {
    const TERM = {
        text: 'text',
        partOfSpeech: 'partOfSpeech',
        definition: 'definition',
        usage: 'usage',
        translation: 'translation',
    };

    let getSelectionBackup;

    beforeAll(() => {
        getSelectionBackup = window.getSelection;
        window.getSelection = () => {
            return {
                toString: () => {},
            };
        };
    });

    afterAll(() => {
        window.getSelection = getSelectionBackup;
    });

    it('renders term correctly', () => {
        const wrapper = shallow(<Term term={TERM} />);

        expect(wrapper.find('li')).toHaveLength(1);
        expect(wrapper.find('.text').text()).toEqual('text');
        expect(wrapper.find('.part-of-speech').text()).toEqual('partOfSpeech');
        expect(wrapper.find('.definition').text()).toEqual('definition');
        expect(wrapper.find('.usage .content').text()).toEqual('usage');
        expect(wrapper.find('.translation').text()).toEqual('translation');
    });

    it('calls the addTextToEditorTranslation function on click', () => {
        const addTextToEditorTranslationFn = sinon.spy();

        const wrapper = shallow(
            <Term
                term={TERM}
                addTextToEditorTranslation={addTextToEditorTranslationFn}
            />,
        );

        wrapper.find('li').simulate('click');
        expect(addTextToEditorTranslationFn.called).toEqual(true);
    });

    it('does not call the addTextToEditorTranslation function if term not translated', () => {
        const term = {
            ...TERM,
            translation: '',
        };
        const addTextToEditorTranslationFn = sinon.spy();

        const wrapper = shallow(
            <Term
                term={term}
                addTextToEditorTranslation={addTextToEditorTranslationFn}
            />,
        );

        wrapper.find('li').simulate('click');
        expect(addTextToEditorTranslationFn.called).toEqual(false);
    });

    it('does not call the addTextToEditorTranslation function if read-only editor', () => {
        const addTextToEditorTranslationFn = sinon.spy();

        const wrapper = shallow(
            <Term
                isReadOnlyEditor={true}
                term={TERM}
                addTextToEditorTranslation={addTextToEditorTranslationFn}
            />,
        );

        wrapper.find('li').simulate('click');
        expect(addTextToEditorTranslationFn.called).toEqual(false);
    });
});
