import classNames from 'classnames';
import React, { useCallback, useEffect, useRef, useState } from 'react';

import type { NotificationState } from '../reducer';

import './NotificationPanel.css';

type Props = {
  notification: NotificationState;
};

/**
 * Show a status notification for a short period of time.
 *
 * This supports showing 'info' (in green) or 'error' (in red) notifications,
 * once at a time. The notification will hide after a 2s timeout, or when
 * clicked.
 */
export function NotificationPanel({
  notification: { message },
}: Props): React.ReactElement<'div'> {
  const [visible, setVisible] = useState(false);
  const timeout = useRef(0);
  const hide = useCallback(() => {
    clearTimeout(timeout.current);
    setVisible(false);
  }, []);

  useEffect(() => {
    clearTimeout(timeout.current);
    if (message) {
      setVisible(true);
      timeout.current = window.setTimeout(hide, 2000);
    } else {
      setVisible(false);
    }
  }, [message]);

  const className = classNames(
    'notification-panel',
    message && visible && 'showing',
  );

  return (
    <div className={className} onClick={hide}>
      <span className={message?.type}>{message?.content}</span>
    </div>
  );
}
