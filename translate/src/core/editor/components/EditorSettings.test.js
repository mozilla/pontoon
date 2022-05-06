import React from 'react';
import { shallow } from 'enzyme';
import sinon from 'sinon';

import { EditorSettings, EditorSettingsDialog } from './EditorSettings';

function createEditorSettingsDialog() {
  const toggleSettingMock = sinon.stub();
  const wrapper = shallow(
    <EditorSettingsDialog
      settings={{
        runQualityChecks: false,
        forceSuggestions: false,
      }}
      toggleSetting={toggleSettingMock}
    />,
  );
  return [wrapper, toggleSettingMock];
}

describe('<EditorSettingsDialog>', () => {
  it('toggles the runQualityChecks setting', () => {
    const [wrapper, toggleSettingMock] = createEditorSettingsDialog();

    // Do it once to turn it on.
    wrapper.find('.menu li').at(0).simulate('click');
    expect(toggleSettingMock.calledOnce).toBeTruthy();
    expect(toggleSettingMock.calledWith('runQualityChecks')).toBeTruthy();

    // Do it twice to turn it off.
    wrapper.setProps({ settings: { runQualityChecks: true } });

    wrapper.find('.menu li').at(0).simulate('click');
    expect(toggleSettingMock.calledTwice).toBeTruthy();
    expect(toggleSettingMock.calledWith('runQualityChecks')).toBeTruthy();
  });

  it('toggles the forceSuggestions setting', () => {
    const [wrapper, toggleSettingMock] = createEditorSettingsDialog();

    // Do it once to turn it on.
    wrapper.find('.menu li').at(1).simulate('click');
    expect(toggleSettingMock.calledOnce).toBeTruthy();
    expect(toggleSettingMock.calledWith('forceSuggestions')).toBeTruthy();

    // Do it twice to turn it off.
    wrapper.setProps({ settings: { forceSuggestions: true } });

    wrapper.find('.menu li').at(1).simulate('click');
    expect(toggleSettingMock.calledTwice).toBeTruthy();
    expect(toggleSettingMock.calledWith('forceSuggestions')).toBeTruthy();
  });
});

describe('<EditorSettings>', () => {
  it('toggles the settings menu when clicking the gear icon', () => {
    const wrapper = shallow(<EditorSettings />);
    expect(wrapper.find('EditorSettingsDialog')).toHaveLength(0);

    wrapper.find('.selector').simulate('click');
    expect(wrapper.find('EditorSettingsDialog')).toHaveLength(1);

    wrapper.find('.selector').simulate('click');
    expect(wrapper.find('EditorSettingsDialog')).toHaveLength(0);
  });
});
