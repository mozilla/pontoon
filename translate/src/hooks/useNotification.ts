import { useState, useEffect } from 'react';
import {
  NotificationMessage,
  BadgeTooltipMessage,
} from '../context/Notification';

export function useNotifications() {
  const [message, setMessage] = useState<NotificationMessage | null>(null);
  const [badgeMessage, setBadgeMessage] = useState<BadgeTooltipMessage | null>(
    null,
  );

  useEffect(() => {
    const rootElt = document.getElementById('root');
    if (rootElt?.dataset.notifications) {
      const notifications = JSON.parse(rootElt.dataset.notifications);
      if (notifications.length > 0) {
        const generalNotification = notifications.find(
          (notification: { type: string }) =>
            notification.type !== 'badge info',
        );
        const badgeNotification = notifications.find(
          (notification: { type: string }) =>
            notification.type === 'badge info',
        );

        if (generalNotification) {
          setMessage({
            type: generalNotification.type,
            content: generalNotification.content,
          });
        }

        if (badgeNotification) {
          const badgeData = JSON.parse(badgeNotification.content);
          setBadgeMessage({
            badgeName: badgeData.name || null,
            badgeLevel: badgeData.level || null,
          });
        }
      }
    }
  }, []);

  return { message, setMessage, badgeMessage, setBadgeMessage };
}
