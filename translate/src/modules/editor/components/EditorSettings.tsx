import { Localized } from '@fluent/react';
import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import { ThemeContext } from '~/context/Theme';
import type { Settings } from '~/modules/user';
import { useOnDiscard } from '~/utils';
import { useTranslator } from '~/hooks/useTranslator';

import './EditorSettings.css';

type Props = {
  settings: Settings;
  updateSetting: (name: keyof Settings, value: boolean) => void;
};

type EditorSettingsProps = {
  settings: Settings;
  toggleSetting: (name: keyof Settings) => void;
  onDiscard: () => void;
};

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
    label: 'Match main interface',
    title: 'Use the same theme as the main appearance',
  },
] as const;

export function EditorSettingsDialog({
  settings,
  toggleSetting,
  onDiscard,
}: EditorSettingsProps): React.ReactElement<'ul'> {
  const ref = useRef<HTMLUListElement>(null);
  const isTranslator = useTranslator();
  const { editorTheme, setEditorTheme } = useContext(ThemeContext);
  useOnDiscard(ref, onDiscard);

  useEffect(() => {
    const mediaQuery = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    ref.current?.scrollIntoView({
      behavior: mediaQuery?.matches ? 'auto' : 'smooth',
      block: 'nearest',
    });
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
          onDiscard={handleDiscard}
        />
      )}
    </div>
  );
}
