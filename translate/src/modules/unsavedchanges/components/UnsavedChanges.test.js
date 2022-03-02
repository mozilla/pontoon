import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { UnsavedChangesBase } from './UnsavedChanges';

import { actions } from '..';

describe('<UnsavedChangesBase>', () => {
    beforeAll(() => {
        sinon.stub(actions, 'hide').returns({ type: 'whatever' });
        sinon.stub(actions, 'ignore').returns({ type: 'whatever' });
    });

    afterEach(() => {
        actions.hide.reset();
        actions.ignore.reset();
    });

    afterAll(() => {
        actions.hide.restore();
        actions.ignore.restore();
    });

    it('renders correctly if shown', () => {
        const wrapper = shallow(
            <UnsavedChangesBase unsavedchanges={{ shown: true }} />,
        );

        expect(wrapper.find('.unsaved-changes')).toHaveLength(1);
        expect(wrapper.find('.close')).toHaveLength(1);
        expect(wrapper.find('.title')).toHaveLength(1);
        expect(wrapper.find('.body')).toHaveLength(1);
        expect(wrapper.find('.proceed.anyway')).toHaveLength(1);
    });

    it('does not render if not shown', () => {
        const wrapper = shallow(
            <UnsavedChangesBase unsavedchanges={{ shown: false }} />,
        );

        expect(wrapper.find('.unsaved-changes')).toHaveLength(0);
    });

    it('closes the unsaved changes popup when the Close button is clicked', () => {
        const wrapper = shallow(
            <UnsavedChangesBase
                unsavedchanges={{ shown: true }}
                dispatch={() => {}}
            />,
        );

        wrapper.find('.close').simulate('click');
        expect(actions.hide.calledOnce).toBeTruthy();
    });

    it('ignores the unsaved changes popup when the Proceed button is clicked', () => {
        const wrapper = shallow(
            <UnsavedChangesBase
                unsavedchanges={{ shown: true }}
                dispatch={() => {}}
            />,
        );

        wrapper.find('.proceed.anyway').simulate('click');
        expect(actions.ignore.calledOnce).toBeTruthy();
    });
});
