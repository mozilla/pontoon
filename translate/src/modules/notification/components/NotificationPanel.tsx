import classNames from 'classnames';
import React, { useCallback, useContext, useEffect, useRef } from 'react';

import { NotificationMessage, ShowNotification } from '~/context/Notification';

import './NotificationPanel.css';

/**
 * Show a status notification for a short period of time.
 *
 * This supports showing 'info' (in green) or 'error' (in red) notifications,
 * once at a time. The notification will hide after a 2s timeout, or when
 * clicked.
 */
export function NotificationPanel(): React.ReactElement<'div'> {
  const message = useContext(NotificationMessage);
  const showNotification = useContext(ShowNotification);

  const timeout = useRef(0);
  const hide = useCallback(() => {
    window.clearTimeout(timeout.current);
    showNotification(null);
  }, []);

  useEffect(() => {
    window.clearTimeout(timeout.current);
    if (message) {
      timeout.current = window.setTimeout(hide, 2000);
    }
  }, [message]);

  const className = classNames('notification-panel', message && 'showing');

  return (
    <div className={className} onClick={hide}>
      <span className={message?.type}>{message?.content}</span>
    </div>
  );
}
