import React from 'react';
import { mount, shallow } from 'enzyme';
import sinon from 'sinon';

import GenericTranslationForm from './GenericTranslationForm';

const DEFAULT_LOCALE = {
    direction: 'ltr',
    code: 'kg',
    script: 'Latin',
};

const EDITOR = {
    translation: 'world',
    errors: [],
    warnings: [],
};

describe('<GenericTranslationForm>', () => {
    it('renders a textarea with some content', () => {
        const wrapper = shallow(
            <GenericTranslationForm editor={EDITOR} locale={DEFAULT_LOCALE} />,
        );

        expect(wrapper.find('textarea')).toHaveLength(1);
        expect(wrapper.find('textarea').html()).toContain('world');
    });

    it('calls the updateTranslation function on change', () => {
        const mockUpdate = sinon.spy();
        const wrapper = shallow(
            <GenericTranslationForm
                editor={EDITOR}
                locale={DEFAULT_LOCALE}
                updateTranslation={mockUpdate}
            />,
        );

        expect(mockUpdate.called).toBeFalsy();
        wrapper
            .find('textarea')
            .simulate('change', { currentTarget: { value: 'good bye' } });
        expect(mockUpdate.called).toBeTruthy();
    });

    it('updates the translation when selectionReplacementContent is passed', () => {
        const resetMock = sinon.stub();
        const updateMock = sinon.stub();

        const wrapper = mount(
            <GenericTranslationForm
                editor={EDITOR}
                locale={DEFAULT_LOCALE}
                unsavedchanges={{ shown: false }}
                resetSelectionContent={resetMock}
                updateTranslation={updateMock}
                updateUnsavedChanges={sinon.stub()}
            />,
        );

        wrapper.setProps({ editor: { selectionReplacementContent: 'hello ' } });

        expect(updateMock.calledOnce).toBeTruthy();
        expect(updateMock.calledWith('hello world')).toBeTruthy();
        expect(resetMock.calledOnce).toBeTruthy();
    });
});
