import { useState, useEffect } from 'react';
import { NotificationMessage } from '~/context/Notification';
import { BadgeTooltipMessage } from '~/context/BadgeTooltip';

export function useNotifications() {
  const [message, setMessage] = useState<NotificationMessage | null>(null);
  const [badgeMessage, setBadgeMessage] = useState<BadgeTooltipMessage | null>(
    null,
  );

  // If there's a notification in the DOM set by Django, show it.
  // Note that we only show it once, and only when the UI has already
  // been rendered, to make sure users do see it.
  useEffect(() => {
    const rootElt = document.getElementById('root');
    if (rootElt?.dataset.notifications) {
      console.log(rootElt?.dataset.notifications);
      const notifications = JSON.parse(rootElt.dataset.notifications);
      if (notifications.length > 0) {
        // Extra tags from the Django messages framework are combined
        // with the level tag into a single string as notification.type
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
