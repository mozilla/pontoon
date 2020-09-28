import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import EditorMainAction from './EditorMainAction';

describe('<EditorMainAction>', () => {
    it('renders the Approve button when an identical translation exists', () => {
        const updateStatus = sinon.mock();
        const params = {
            isTranslator: true,
            sameExistingTranslation: { pk: 1 },
            updateTranslationStatus: updateStatus,
        };
        const wrapper = shallow(<EditorMainAction {...params} />);

        expect(wrapper.find('.action-approve')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-save')).toHaveLength(0);

        wrapper.find('.action-approve').simulate('click');
        expect(updateStatus.calledWith(1, 'approve')).toBeTruthy();
    });

    it('renders the Suggest button when force suggestion is on', () => {
        const params = {
            isTranslator: true,
            forceSuggestions: true,
        };
        const wrapper = shallow(<EditorMainAction {...params} />);

        expect(wrapper.find('.action-suggest')).toHaveLength(1);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
        expect(wrapper.find('.action-save')).toHaveLength(0);
    });

    it('renders the Suggest button when user does not have permission', () => {
        const params = {
            isTranslator: false,
        };
        const wrapper = shallow(<EditorMainAction {...params} />);

        expect(wrapper.find('.action-suggest')).toHaveLength(1);
        expect(wrapper.find('.action-save')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
    });

    it('shows a spinner and a disabled Suggesting button when running request', () => {
        const params = {
            isTranslator: true,
            forceSuggestions: true,
            isRunningRequest: true,
        };
        const wrapper = shallow(<EditorMainAction {...params} />);

        expect(wrapper.find('.action-suggest')).toHaveLength(1);
        expect(wrapper.find('.action-suggest .fa-spin')).toHaveLength(1);
    });

    it('renders the Save button when force suggestion is off', () => {
        const params = {
            isTranslator: true,
            forceSuggestions: false,
        };
        const wrapper = shallow(<EditorMainAction {...params} />);

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
    });

    it('renders the Save button when translation is not the same', () => {
        const params = {
            isTranslator: true,
            sameExistingTranslation: null,
        };
        const wrapper = shallow(<EditorMainAction {...params} />);

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
    });

    it('shows a spinner and a disabled Saving button when running request', () => {
        const params = {
            isTranslator: true,
            isRunningRequest: true,
        };
        const wrapper = shallow(<EditorMainAction {...params} />);

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-save .fa-spin')).toHaveLength(1);
    });
});
