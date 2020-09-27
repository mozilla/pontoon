import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { EditorSettingsBase } from './EditorSettings';

function createEditorSettings() {
    const updateSettingMock = sinon.stub();
    const wrapper = shallow(
        <EditorSettingsBase
            settings={{
                runQualityChecks: false,
                forceSuggestions: false,
            }}
            updateSetting={updateSettingMock}
        />,
    );
    return [wrapper, updateSettingMock];
}

describe('<EditorSettings>', () => {
    it('toggles the runQualityChecks setting', () => {
        const [wrapper, updateSettingMock] = createEditorSettings();

        // Do it once to turn it on.
        wrapper.find('.selector').simulate('click');
        wrapper.find('.menu li').at(0).simulate('click');
        expect(updateSettingMock.calledOnce).toBeTruthy();
        expect(
            updateSettingMock.calledWith('runQualityChecks', true),
        ).toBeTruthy();

        // Do it twice to turn it off.
        wrapper.setProps({ settings: { runQualityChecks: true } });

        wrapper.find('.selector').simulate('click');
        wrapper.find('.menu li').at(0).simulate('click');
        expect(updateSettingMock.calledTwice).toBeTruthy();
        expect(
            updateSettingMock.calledWith('runQualityChecks', false),
        ).toBeTruthy();
    });

    it('toggles the forceSuggestions setting', () => {
        const [wrapper, updateSettingMock] = createEditorSettings();

        // Do it once to turn it on.
        wrapper.find('.selector').simulate('click');
        wrapper.find('.menu li').at(1).simulate('click');
        expect(updateSettingMock.calledOnce).toBeTruthy();
        expect(
            updateSettingMock.calledWith('forceSuggestions', true),
        ).toBeTruthy();

        // Do it twice to turn it off.
        wrapper.setProps({ settings: { forceSuggestions: true } });

        wrapper.find('.selector').simulate('click');
        wrapper.find('.menu li').at(1).simulate('click');
        expect(updateSettingMock.calledTwice).toBeTruthy();
        expect(
            updateSettingMock.calledWith('forceSuggestions', false),
        ).toBeTruthy();
    });
});
