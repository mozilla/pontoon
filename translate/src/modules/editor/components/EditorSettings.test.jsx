import React from 'react';
import { shallow } from 'enzyme';

import { EditorSettings, EditorSettingsDialog } from './EditorSettings';
import { vi } from 'vitest';

vi.mock('react', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useContext: () => ({ code: 'en' }),
  };
});

vi.mock('~/modules/project/hooks', () => ({
  useProject: () => ({ slug: 'test' }),
}));

vi.mock('react-redux', () => ({
  ...vi.importActual('react-redux'),
  useSelector: (selector) =>
    selector({
      user: {
        isAuthenticated: true,
        canManageLocales: ['en'],
      },
    }),
}));

function createEditorSettingsDialogForNonTranslator() {
  vi.mock('~/hooks/useTranslator', () => ({
    useTranslator: () => false,
  }));

  const toggleSettingMock = vi.fn();
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

function createEditorSettingsDialog() {
  const toggleSettingMock = vi.fn();
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
  beforeEach(() => {
    vi.unmock('~/hooks/useTranslator');
  });

  it('does not show the forceSuggestions setting if user is not a translator', () => {
    const [wrapper] = createEditorSettingsDialogForNonTranslator();

    expect(wrapper.find('.menu li').at(1).text()).not.toContain(
      'Force suggestions',
    );
  });

  it('toggles the runQualityChecks setting', () => {
    const [wrapper, toggleSettingMock] = createEditorSettingsDialog();

    // Do it once to turn it on.
    wrapper.find('.menu li').at(0).simulate('click');
    expect(toggleSettingMock).toHaveBeenCalledOnce();
    expect(toggleSettingMock).toHaveBeenCalledWith('runQualityChecks');

    // Do it twice to turn it off.
    wrapper.setProps({ settings: { runQualityChecks: true } });

    wrapper.find('.menu li').at(0).simulate('click');
    expect(toggleSettingMock).toHaveBeenCalledTimes(2);
    expect(toggleSettingMock).toHaveBeenCalledWith('runQualityChecks');
  });

  it('toggles the forceSuggestions setting', () => {
    const [wrapper, toggleSettingMock] = createEditorSettingsDialog();

    // Do it once to turn it on.
    wrapper.find('.menu li').at(1).simulate('click');
    expect(toggleSettingMock).toHaveBeenCalledOnce();
    expect(toggleSettingMock).toHaveBeenCalledWith('forceSuggestions');

    // Do it twice to turn it off.
    wrapper.setProps({ settings: { forceSuggestions: true } });

    wrapper.find('.menu li').at(1).simulate('click');
    expect(toggleSettingMock).toHaveBeenCalledTimes(2);
    expect(toggleSettingMock).toHaveBeenCalledWith('forceSuggestions');
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
