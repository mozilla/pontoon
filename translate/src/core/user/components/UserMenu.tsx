import { Localized } from '@fluent/react';
import React, { useRef, useState } from 'react';

import type { NavigationParams } from '~/core/navigation';
import type { UserState } from '~/core/user';
import { useOnDiscard } from '~/core/utils';

import FileUpload from './FileUpload';
import SignOut from './SignOut';

import './UserMenu.css';

type Props = {
  isReadOnly: boolean;
  isTranslator: boolean;
  parameters: NavigationParams;
  signOut: () => void;
  user: UserState;
};

type UserMenuProps = Props & {
  onDiscard: () => void;
};

export function UserMenu({
  user,
  parameters,
  isTranslator,
  isReadOnly,
  signOut,
  onDiscard,
}: UserMenuProps): React.ReactElement<'ul'> {
  const { locale, project, resource } = parameters;

  const canDownload =
    project !== 'all-projects' && resource !== 'all-resources';

  /* TODO: Also disable for subpages (in-context l10n) when supported */
  const canUpload = canDownload && isTranslator && !isReadOnly;

  const ref = useRef<HTMLUListElement>(null);
  useOnDiscard(ref, onDiscard);

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
          <FileUpload parameters={parameters} />
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
            <SignOut signOut={signOut} />
          </li>
        </>
      )}
    </ul>
  );
}

export default function UserMenuBase(props: Props): React.ReactElement<'div'> {
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

      {visible && <UserMenu {...props} onDiscard={() => setVisible(false)} />}
    </div>
  );
}
