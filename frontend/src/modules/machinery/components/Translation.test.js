import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import Translation from './Translation';

describe('<Translation>', () => {
    const ORIGINAL = 'A horse, a horse! My kingdom for a horse!';
    const DEFAULT_TRANSLATION = {
        sources: [
            {
                type: 'translation-memory',
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

    it('renders a translation correctly', () => {
        const wrapper = shallow(
            <Translation
                translation={DEFAULT_TRANSLATION}
                locale={DEFAULT_LOCALE}
                entity={DEFAULT_ENTITY}
            />,
        );

        expect(
            wrapper.find('.original').find('GenericTranslation'),
        ).toHaveLength(1);
        expect(
            wrapper.find('.suggestion').find('GenericTranslation').props()
                .content,
        ).toContain('Un cheval, un cheval !');

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
        const wrapper = shallow(
            <Translation
                translation={translation}
                locale={DEFAULT_LOCALE}
                entity={DEFAULT_ENTITY}
            />,
        );

        expect(wrapper.find('.quality')).toHaveLength(1);
        expect(wrapper.find('.quality').text()).toEqual('100%');
    });

    it('updateMachinerySources is called while copying', () => {
        const translationMock = sinon.stub();
        const machineryMock = sinon.stub();

        const wrapper = shallow(
            <Translation
                translation={DEFAULT_TRANSLATION}
                locale={DEFAULT_LOCALE}
                entity={DEFAULT_ENTITY}
                updateEditorTranslation={translationMock}
                updateMachinerySources={machineryMock}
            />,
        );

        expect(machineryMock.calledOnce).toBeFalsy();
        wrapper.find('li.translation').simulate('click');
        expect(machineryMock.calledOnce).toBeTruthy();
        expect(
            machineryMock.calledWith(
                DEFAULT_TRANSLATION.sources,
                DEFAULT_TRANSLATION.translation,
            ),
        ).toBeTruthy();
    });
});
