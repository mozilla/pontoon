import { Localized } from '@fluent/react';
import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import type { MachineryAutocomplete } from '~/api/user';
import { ThemeContext } from '~/context/Theme';
import type { Settings } from '~/modules/user';
import type { SettingsState } from '~/modules/user/reducer';
import { useOnDiscard } from '~/utils';
import { scrollIntoView } from '~/utils/scrollIntoView';
import { useTranslator } from '~/hooks/useTranslator';

import './EditorSettings.css';

type Props = {
  settings: SettingsState;
  updateSetting: (name: keyof Settings, value: boolean) => void;
  updateMachineryAutocomplete: (value: MachineryAutocomplete) => void;
};

type EditorSettingsProps = {
  settings: SettingsState;
  toggleSetting: (name: keyof Settings) => void;
  updateMachineryAutocomplete: (value: MachineryAutocomplete) => void;
  onDiscard: () => void;
};

const AUTOCOMPLETE_OPTIONS = [
  {
    value: 'off',
    id: 'editor-EditorSettings--autocomplete-off',
    label: 'Off',
    title: 'Do not autocomplete from Machinery',
  },
  {
    value: 'word',
    id: 'editor-EditorSettings--autocomplete-word',
    label: 'Word',
    title: 'Autocomplete from Machinery one word at a time',
  },
  {
    value: 'full',
    id: 'editor-EditorSettings--autocomplete-full',
    label: 'Full',
    title: 'Autocomplete the rest of a Machinery translation',
  },
] as const;

const EDITOR_THEME_OPTIONS = [
  {
    value: 'dark',
    id: 'editor-EditorSettings--theme-dark',
    icon: 'far fa-moon',
    label: 'Dark',
    title: 'Use a dark editor',
  },
  {
    value: 'light',
    id: 'editor-EditorSettings--theme-light',
    icon: 'fas fa-sun',
    label: 'Light',
    title: 'Use a light editor',
  },
  {
    value: 'match',
    id: 'editor-EditorSettings--theme-match',
    icon: 'fas fa-link',
    label: 'Main',
    title: 'Use a theme that matches the main interface',
  },
] as const;

export function EditorSettingsDialog({
  settings,
  toggleSetting,
  updateMachineryAutocomplete,
  onDiscard,
}: EditorSettingsProps): React.ReactElement<'ul'> {
  const ref = useRef<HTMLUListElement>(null);
  const isTranslator = useTranslator();
  const { editorTheme, setEditorTheme } = useContext(ThemeContext);
  useOnDiscard(ref, onDiscard);

  useEffect(() => {
    scrollIntoView(ref.current);
  });

  return (
    <ul ref={ref} className='menu'>
      <Localized
        id='editor-EditorSettings--toolkit-checks'
        attrs={{ title: true }}
        elems={{ glyph: <i className='fas fa-fw' /> }}
      >
        <li
          className={
            'check-box' + (settings.runQualityChecks ? ' enabled' : '')
          }
          title='Run Translate Toolkit checks before submitting translations'
          onClick={() => toggleSetting('runQualityChecks')}
        >
          {'<glyph></glyph>Translate Toolkit checks'}
        </li>
      </Localized>

      {isTranslator ? (
        <Localized
          id='editor-EditorSettings--force-suggestions'
          attrs={{ title: true }}
          elems={{ glyph: <i className='fas fa-fw' /> }}
        >
          <li
            className={
              'check-box' + (settings.forceSuggestions ? ' enabled' : '')
            }
            title='Save suggestions instead of translations'
            onClick={() => toggleSetting('forceSuggestions')}
          >
            {'<glyph></glyph>Make suggestions'}
          </li>
        </Localized>
      ) : null}

      <li className='horizontal-separator'></li>
      <div className='appearance'>
        <Localized id='editor-EditorSettings--autocomplete-title'>
          <p className='help'>{'Autocomplete'}</p>
        </Localized>
        <span className='toggle-button'>
          {AUTOCOMPLETE_OPTIONS.map(({ value, id, label, title }) => (
            <Localized key={value} id={id} attrs={{ title: true }}>
              <button
                type='button'
                value={value}
                className={`${value} ${settings.machineryAutocomplete === value ? 'active' : ''}`}
                title={title}
                onClick={() => updateMachineryAutocomplete(value)}
              >
                {label}
              </button>
            </Localized>
          ))}
        </span>
      </div>

      <li className='horizontal-separator'></li>
      <div className='appearance'>
        <Localized id='editor-EditorSettings--theme-title'>
          <p className='help'>{'Editor theme'}</p>
        </Localized>
        <span className='toggle-button'>
          {EDITOR_THEME_OPTIONS.map(({ value, id, icon, label, title }) => (
            <Localized
              key={value}
              id={id}
              attrs={{ title: true }}
              elems={{ glyph: <i className={`icon ${icon}`} /> }}
            >
              <button
                type='button'
                value={value}
                className={`${value} ${editorTheme === value ? 'active' : ''}`}
                title={title}
                onClick={() => setEditorTheme(value)}
              >
                {`<glyph></glyph> ${label}`}
              </button>
            </Localized>
          ))}
        </span>
      </div>

      <li className='horizontal-separator'></li>
      <li>
        <Localized id='editor-EditorSettings--change-all'>
          <a href='/settings/'>{'Change all settings'}</a>
        </Localized>
      </li>
    </ul>
  );
}

/*
 * Renders settings to be used to customize interactions with the Editor.
 */
export function EditorSettings({
  settings,
  updateSetting,
  updateMachineryAutocomplete,
}: Props): React.ReactElement<'div'> {
  const [visible, setVisible] = useState(false);
  const toggleVisible = useCallback(() => setVisible((prev) => !prev), []);
  const handleDiscard = useCallback(() => setVisible(false), []);

  const toggleSetting = useCallback(
    (name: keyof Settings) => {
      updateSetting(name, !settings[name]);
      toggleVisible();
    },
    [settings, updateSetting],
  );

  return (
    <div className='editor-settings'>
      <div
        className='selector fas fa-cog'
        role='button'
        title='Settings'
        onClick={toggleVisible}
      />

      {visible && (
        <EditorSettingsDialog
          settings={settings}
          toggleSetting={toggleSetting}
          updateMachineryAutocomplete={updateMachineryAutocomplete}
          onDiscard={handleDiscard}
        />
      )}
    </div>
  );
}
