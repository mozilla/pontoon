import React from 'react';
import { Localized } from '@fluent/react';

import './UserAvatar.css';

type Props = {
  username: string | null;
  title?: string;
  imageUrl: string | null;
  userBanner: string[] | null;
};

const DELETED_USER_AVATAR =
  'data:image/svg+xml,' +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="44" height="44" viewBox="0 0 44 44">' +
      '<rect width="44" height="44" rx="4" fill="#aaa"/>' +
      '<text x="22" y="30" font-size="24" text-anchor="middle" fill="#fff">?</text>' +
      '</svg>',
  );

export function UserAvatar(props: Props): React.ReactElement<'div'> {
  const { username, title, imageUrl, userBanner } = props;
  const [status, tooltip] = userBanner ?? ['', ''];

  const avatarImage = (
    <div className='avatar-container'>
      <Localized id='user-UserAvatar--alt-text' attrs={{ alt: true }}>
        <img
          src={imageUrl ?? DELETED_USER_AVATAR}
          alt='User Profile'
          height='44'
          width='44'
        />
      </Localized>
      {status && (
        <span className={`user-banner ${status}`} title={tooltip}>
          {status}
        </span>
      )}
    </div>
  );

  return (
    <div className='user-avatar'>
      {username ? (
        <a
          href={`/contributors/${username}`}
          title={title}
          target='_blank'
          rel='noopener noreferrer'
          onClick={(e: React.MouseEvent) => e.stopPropagation()}
        >
          {avatarImage}
        </a>
      ) : (
        avatarImage
      )}
    </div>
  );
}
