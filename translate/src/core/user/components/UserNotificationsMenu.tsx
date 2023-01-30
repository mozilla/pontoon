import { Localized } from '@fluent/react';
import React, { useCallback, useEffect, useRef, useState } from 'react';

import { logUXAction } from '~/api/uxaction';
import { useOnDiscard } from '~/utils';

import type { Notification, UserState } from '../index';
import { UserNotification } from './UserNotification';
import './UserNotificationsMenu.css';

type Props = {
  markAllNotificationsAsRead: () => void;
  user: UserState;
};

type UserNotificationsMenuProps = {
  notifications: Array<Notification>;
  onDiscard: () => void;
};

export function UserNotificationsMenuDialog({
  notifications,
  onDiscard,
}: UserNotificationsMenuProps): React.ReactElement<'div'> {
  const ref = useRef(null);
  useOnDiscard(ref, onDiscard);

  return (
    <div ref={ref} className='menu'>
      <ul className='notification-list'>
        {notifications.length ? (
          notifications.map((notification) => {
            return (
              <UserNotification
                notification={notification}
                key={notification.id}
              />
            );
          })
        ) : (
          <li className='no'>
            <i className='icon fa fa-bell fa-fw'></i>
            <Localized id='user-UserNotificationsMenu--no-notifications-title'>
              <p className='title'>No new notifications.</p>
            </Localized>
            <Localized id='user-UserNotificationsMenu--no-notifications-description'>
              <p className='description'>
                Here you’ll see updates for localizations you contribute to.
              </p>
            </Localized>
          </li>
        )}
      </ul>

      <div className='see-all'>
        <Localized id='user-UserNotificationsMenu--see-all-notifications'>
          <a href='/notifications?referrer=ui'>See all Notifications</a>
        </Localized>
      </div>
    </div>
  );
}

/**
 * Renders user notifications.
 */
export function UserNotificationsMenu({
  markAllNotificationsAsRead,
  user,
}: Props): null | React.ReactElement<'div'> {
  const [visible, setVisible] = useState(false);
  const handleDiscard = useCallback(() => setVisible(false), []);

  const unread = user?.notifications.has_unread;

  useEffect(() => {
    if (user.isAuthenticated && unread) {
      logUXAction('Render: Unread notifications icon', 'Notifications 1.0', {
        pathname: window.location.pathname,
      });
    }
  }, []);

  const handleClick = useCallback(() => {
    if (visible) {
      setVisible(false);
    } else {
      setVisible(true);
      logUXAction('Click: Notifications icon', 'Notifications 1.0', {
        pathname: window.location.pathname,
        unread,
      });
    }
    if (unread) {
      markAllNotificationsAsRead();
    }
  }, [markAllNotificationsAsRead, unread, visible]);

  return user?.isAuthenticated ? (
    <div className='user-notifications-menu'>
      <div className='selector' onClick={handleClick}>
        <i className='icon far fa-bell fa-fw'></i>
        {unread && <i className='badge'>{user.notifications.unread_count}</i>}
      </div>

      {visible && (
        <UserNotificationsMenuDialog
          notifications={user.notifications.notifications}
          onDiscard={handleDiscard}
        />
      )}
    </div>
  ) : null;
}
