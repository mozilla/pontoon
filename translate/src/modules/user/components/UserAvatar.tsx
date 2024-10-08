import React from 'react';
import { Localized } from '@fluent/react';

type Props = {
  username: string;
  title?: string;
  imageUrl: string;
  userStatus?: string;
};

export function UserAvatar(props: Props): React.ReactElement<'div'> {
  const { username, title, imageUrl, userStatus } = props;
  console.log(userStatus);

  return (
    <div className='user-avatar'>
      <a
        href={`/contributors/${username}`}
        title={title}
        target='_blank'
        rel='noopener noreferrer'
        onClick={(e: React.MouseEvent) => e.stopPropagation()}
      >
        <div className='avatar-container'>
          <Localized id='user-UserAvatar--alt-text' attrs={{ alt: true }}>
            <img src={imageUrl} alt='User Profile' height='44' width='44' />
          </Localized>
          {userStatus && (
            <Localized id='user-UserAvatar--userStatus' vars={{ userStatus }}>
              <span className='user-status-banner' title='{$userStatus}'>
                {userStatus}
              </span>
            </Localized>
          )}
        </div>
      </a>
    </div>
  );
}
