import { Localized } from '@fluent/react';
import React, { useContext, useRef, useState, useEffect } from 'react';

import { EntityView } from '~/context/EntityView';
import { Location } from '~/context/Location';
import { useOnDiscard } from '~/utils';
import { useTranslator } from '~/hooks/useTranslator';

import type { UserState } from '../index';
import { FileUpload } from './FileUpload';
import { SignInOutForm } from './SignInOutForm';

import './UserMenu.css';

type Props = {
  user: UserState;
  theme: string;
  onThemeChange: (theme: string) => void;
};

type UserMenuProps = Props & {
  onDiscard: () => void;
};

export function UserMenuDialog({
  onDiscard,
  user,
  onThemeChange,
}: UserMenuProps): React.ReactElement<'ul'> {
  const isTranslator = useTranslator();
  const { entity } = useContext(EntityView);

  const location = useContext(Location);
  const { locale, project, resource } = location;

  const canDownload =
    project !== 'all-projects' && resource !== 'all-resources';
  const canUpload = canDownload && isTranslator && !entity.readonly;

  const ref = useRef<HTMLUListElement>(null);
  useOnDiscard(ref, onDiscard);

  const [theme, setTheme] = useState<string>(
    () => document.body.getAttribute('data-theme') || 'dark',
  );

  function getSystemTheme() {
    if (
      window.matchMedia &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    ) {
      return 'dark';
    } else {
      return 'light';
    }
  }

  useEffect(() => {
    function applyTheme(newTheme: string) {
      if (newTheme === 'system') {
        newTheme = getSystemTheme();
      }
      document.body.classList.remove(
        'dark-theme',
        'light-theme',
        'system-theme',
      );
      document.body.classList.add(`${newTheme}-theme`);
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    function handleThemeChange(e: MediaQueryListEvent) {
      let userThemeSetting = document.body.getAttribute('data-theme') || 'dark';

      if (userThemeSetting === 'system') {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    }

    mediaQuery.addEventListener('change', handleThemeChange);

    applyTheme(theme);

    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange);
    };
  }, [theme]);

  const handleThemeButtonClick = (selectedTheme: string) => {
    setTheme(selectedTheme); // Update the local state
    onThemeChange(selectedTheme); // Save theme to the database
  };

  return (
    <ul ref={ref} className='menu'>
      {user.isAuthenticated && (
        <>
          <li className='details'>
            <a href={`/contributors/${user.username}/`}>
              <img src={user.gravatarURLBig} alt='' height='88' width='88' />
              <p className='name'>{user.nameOrEmail}</p>
              <p className='email'>{user.email}</p>
            </a>
          </li>
          <li className='horizontal-separator'></li>

          <p className='help'>Choose appearance</p>
          <span className='toggle-button'>
            <button
              type='button'
              value='dark'
              className={`dark ${theme === 'dark' ? 'active' : ''}`}
              title='Use a dark theme'
              onClick={() => handleThemeButtonClick('dark')}
            >
              <i className='icon far fa-moon'></i>Dark
            </button>
            <button
              type='button'
              value='light'
              className={`light ${theme === 'light' ? 'active' : ''}`}
              title='Use a light theme'
              onClick={() => handleThemeButtonClick('light')}
            >
              <i className='icon fa fa-sun'></i>Light
            </button>
            <button
              type='button'
              value='system'
              className={`system ${theme === 'system' ? 'active' : ''}`}
              title='Use a theme that matches your system settings'
              onClick={() => handleThemeButtonClick('system')}
            >
              <i className='icon fa fa-laptop'></i>System
            </button>
          </span>

          <li className='horizontal-separator'></li>
        </>
      )}

      <li>
        <Localized
          id='user-UserMenu--download-terminology'
          elems={{ glyph: <i className='fa fa-cloud-download-alt fa-fw' /> }}
        >
          <a href={`/terminology/${locale}.tbx`}>
            {'<glyph></glyph>Download Terminology'}
          </a>
        </Localized>
      </li>

      <li>
        <Localized
          id='user-UserMenu--download-tm'
          elems={{ glyph: <i className='fa fa-cloud-download-alt fa-fw' /> }}
        >
          <a href={`/translation-memory/${locale}.${project}.tmx`}>
            {'<glyph></glyph>Download Translation Memory'}
          </a>
        </Localized>
      </li>

      {canDownload && (
        <li>
          <Localized
            id='user-UserMenu--download-translations'
            elems={{ glyph: <i className='fa fa-cloud-download-alt fa-fw' /> }}
          >
            <a
              href={`/translations/?code=${locale}&slug=${project}&part=${resource}`}
            >
              {'<glyph></glyph>Download Translations'}
            </a>
          </Localized>
        </li>
      )}

      {canUpload && (
        <li>
          <FileUpload parameters={location} />
        </li>
      )}

      <li className='horizontal-separator'></li>

      <li>
        <Localized
          id='user-UserMenu--terms'
          elems={{ glyph: <i className='fa fa-gavel fa-fw' /> }}
        >
          <a href='/terms/' rel='noopener noreferrer' target='_blank'>
            {'<glyph></glyph>Terms of Use'}
          </a>
        </Localized>
      </li>

      <li>
        <Localized
          id='user-UserMenu--github'
          elems={{ glyph: <i className='fab fa-github fa-fw' /> }}
        >
          <a
            href='https://github.com/mozilla/pontoon/'
            rel='noopener noreferrer'
            target='_blank'
          >
            {'<glyph></glyph>Hack it on GitHub'}
          </a>
        </Localized>
      </li>

      <li>
        <Localized
          id='user-UserMenu--feedback'
          elems={{ glyph: <i className='fa fa-comment-dots fa-fw' /> }}
        >
          <a
            href='https://discourse.mozilla.org/c/pontoon'
            rel='noopener noreferrer'
            target='_blank'
          >
            {'<glyph></glyph>Give Feedback'}
          </a>
        </Localized>
      </li>

      <li>
        <Localized
          id='user-UserMenu--help'
          elems={{ glyph: <i className='fa fa-life-ring fa-fw' /> }}
        >
          <a
            href='https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/'
            rel='noopener noreferrer'
            target='_blank'
          >
            {'<glyph></glyph>Help'}
          </a>
        </Localized>
      </li>

      {user.isAuthenticated && <li className='horizontal-separator'></li>}

      {user.isAdmin && (
        <>
          <li>
            <Localized
              id='user-UserMenu--admin'
              elems={{ glyph: <i className='fa fa-wrench fa-fw' /> }}
            >
              <a href='/admin/'>{'<glyph></glyph>Admin'}</a>
            </Localized>
          </li>
          {project !== 'all-projects' && (
            <li>
              <Localized
                id='user-UserMenu--admin-project'
                elems={{ glyph: <i className='fa fa-wrench fa-fw' /> }}
              >
                <a href={`/admin/projects/${project}/`}>
                  {'<glyph></glyph>Admin · Current Project'}
                </a>
              </Localized>
            </li>
          )}
        </>
      )}

      {user.isAuthenticated && (
        <>
          <li>
            <Localized
              id='user-UserMenu--settings'
              elems={{ glyph: <i className='fa fa-cog fa-fw' /> }}
            >
              <a href='/settings/'>{'<glyph></glyph>Settings'}</a>
            </Localized>
          </li>
          <li>
            <Localized
              id='user-SignOut--sign-out'
              elems={{ glyph: <i className='fa fa-sign-out-alt fa-fw' /> }}
            >
              <SignInOutForm url={user.signOutURL}>
                {'<glyph></glyph>Sign out'}
              </SignInOutForm>
            </Localized>
          </li>
        </>
      )}
    </ul>
  );
}

export function UserMenu(props: Props): React.ReactElement<'div'> {
  const [visible, setVisible] = useState(false);
  return (
    <div className='user-menu'>
      <div
        className='selector'
        onClick={() => setVisible((visible) => !visible)}
      >
        {props.user.isAuthenticated ? (
          <img
            src={props.user.gravatarURLSmall}
            alt=''
            height='44'
            width='44'
          />
        ) : (
          <div className='menu-icon fa fa-bars' />
        )}
      </div>

      {visible && (
        <UserMenuDialog {...props} onDiscard={() => setVisible(false)} />
      )}
    </div>
  );
}
