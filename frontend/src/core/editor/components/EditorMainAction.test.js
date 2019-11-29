import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import EditorMainAction from './EditorMainAction';


const HISTORY = {
    translations: [
        {
            pk: 12,
            string: 'I was there before',
            approved: false,
        },
        {
            pk: 98,
            string: 'hello, world!',
            approved: true,
        }
    ],
};

describe('<EditorMainAction>', () => {
    it('renders the Approve button when translation is same as initial', () => {
        const updateStatus = sinon.mock();
        const params = {
            activeTranslation: { pk: 1, string: 'something' },
            initialTranslation: 'something',
            isTranslator: true,
            history: HISTORY,
            translation: 'something',
            updateTranslationStatus: updateStatus,
        }
        const wrapper = shallow(<EditorMainAction { ...params } />);

        expect(wrapper.find('.action-approve')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-save')).toHaveLength(0);

        wrapper.find('.action-approve').simulate('click');

        expect(updateStatus.calledWith(1, 'approve')).toBeTruthy();
    });

    it('renders the Approve button when translation is same as one in history', () => {
        const params = {
            initialTranslation: 'something',
            isTranslator: true,
            history: HISTORY,
            translation: 'I was there before',
        }
        const wrapper = shallow(<EditorMainAction { ...params } />);

        expect(wrapper.find('.action-approve')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-save')).toHaveLength(0);
    });

    it('renders the Suggest button when force suggestion is on', () => {
        const params = {
            isTranslator: false,
            forceSuggestions: true,
        }
        const wrapper = shallow(<EditorMainAction { ...params } />);

        expect(wrapper.find('.action-suggest')).toHaveLength(1);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
        expect(wrapper.find('.action-save')).toHaveLength(0);
    });

    it('renders the Save button when force suggestion is off', () => {
        const params = {
            isTranslator: false,
            forceSuggestions: false,
        }
        const wrapper = shallow(<EditorMainAction { ...params } />);

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
    });

    it('renders the Save button when translation is not the same', () => {
        const params = {
            initialTranslation: 'something',
            isTranslator: true,
            history: HISTORY,
            translation: 'something else',
        }
        const wrapper = shallow(<EditorMainAction { ...params } />);

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
    });

    it('renders the Save button when same translation exists but is approved', () => {
        const params = {
            initialTranslation: 'something',
            isTranslator: true,
            history: HISTORY,
            translation: 'hello, world!',
        }
        const wrapper = shallow(<EditorMainAction { ...params } />);

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
    });

    it('renders the Save button when user does not have permission', () => {
        const params = {
            initialTranslation: 'something',
            isTranslator: false,
            history: HISTORY,
            translation: 'something',
        }
        const wrapper = shallow(<EditorMainAction { ...params } />);

        expect(wrapper.find('.action-save')).toHaveLength(1);
        expect(wrapper.find('.action-suggest')).toHaveLength(0);
        expect(wrapper.find('.action-approve')).toHaveLength(0);
    });
});
