import React from 'react';

import { EditorSettings, EditorSettingsDialog } from './EditorSettings';
import { beforeAll, vi } from 'vitest';
import { fireEvent, render } from '@testing-library/react';
import { MockLocalizationProvider } from '~/test/utils';

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
  const wrapper = render(
    <MockLocalizationProvider>
      <EditorSettingsDialog
        settings={{
          runQualityChecks: false,
          forceSuggestions: false,
        }}
        toggleSetting={toggleSettingMock}
      />
    </MockLocalizationProvider>,
  );
  return [wrapper, toggleSettingMock];
}

function createEditorSettingsDialog() {
  const toggleSettingMock = vi.fn();
  const wrapper = render(
    <MockLocalizationProvider>
      <EditorSettingsDialog
        settings={{
          runQualityChecks: false,
          forceSuggestions: false,
        }}
        toggleSetting={toggleSettingMock}
      />
    </MockLocalizationProvider>,
  );
  return [wrapper, toggleSettingMock];
}

describe('<EditorSettingsDialog>', () => {
  beforeAll(() => {
    window.HTMLElement.prototype.scrollIntoView = vi.fn();
  });
  beforeEach(() => {
    vi.unmock('~/hooks/useTranslator');
  });

  it('does not show the forceSuggestions setting if user is not a translator', () => {
    const [{ getAllByRole }] = createEditorSettingsDialogForNonTranslator();

    expect(getAllByRole('listitem')[1].textContent).not.toContain(
      'Force suggestions',
    );
  });

  it('toggles the runQualityChecks setting', () => {
    const [{ getAllByRole, rerender }, toggleSettingMock] =
      createEditorSettingsDialog();

    // Do it once to turn it on.
    fireEvent.click(getAllByRole('listitem')[0]);
    expect(toggleSettingMock.mock.calls).toMatchObject([['runQualityChecks']]);

    // Do it twice to turn it off.
    rerender(
      <MockLocalizationProvider>
        <EditorSettingsDialog
          settings={{
            runQualityChecks: true,
            forceSuggestions: false,
          }}
          toggleSetting={toggleSettingMock}
        />
      </MockLocalizationProvider>,
    );

    fireEvent.click(getAllByRole('listitem')[0]);
    expect(toggleSettingMock).toHaveBeenCalledTimes(2);
    expect(toggleSettingMock).toHaveBeenCalledWith('runQualityChecks');
  });

  it('toggles the forceSuggestions setting', () => {
    const [{ getAllByRole, rerender }, toggleSettingMock] =
      createEditorSettingsDialog();

    // Do it once to turn it on.
    fireEvent.click(getAllByRole('listitem')[1]);
    expect(toggleSettingMock.mock.calls).toMatchObject([['forceSuggestions']]);

    // Do it twice to turn it off.
    rerender(
      <MockLocalizationProvider>
        <EditorSettingsDialog
          settings={{
            runQualityChecks: false,
            forceSuggestions: true,
          }}
          toggleSetting={toggleSettingMock}
        />
      </MockLocalizationProvider>,
    );

    fireEvent.click(getAllByRole('listitem')[1]);
    expect(toggleSettingMock).toHaveBeenCalledTimes(2);
    expect(toggleSettingMock).toHaveBeenCalledWith('forceSuggestions');
  });
});

describe('<EditorSettings>', () => {
  it('toggles the settings menu when clicking the gear icon', () => {
    const { getByRole, queryByRole } = render(
      <MockLocalizationProvider>
        <EditorSettings settings={{}} />
      </MockLocalizationProvider>,
    );
    expect(queryByRole('list')).toBeNull();

    fireEvent.click(getByRole('button', { name: /SETTINGS/i }));
    expect(queryByRole('list')).toBeInTheDocument();

    fireEvent.click(getByRole('button', { name: /SETTINGS/i }));
    expect(queryByRole('list')).toBeNull();
  });
});
