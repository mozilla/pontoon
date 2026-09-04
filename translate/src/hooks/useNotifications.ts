import { useState, useEffect } from 'react';
import { NotificationMessage } from '~/context/Notification';
import { BadgeTooltipMessage } from '~/context/BadgeTooltip';

/** Display summaries for longer than standard (2s), since they carry
 * more information than a status message. */
const UPLOAD_MESSAGE_DURATION = 6000;

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
      const notifications = JSON.parse(rootElt.dataset.notifications);
      if (notifications.length > 0) {
        // Extra tags from the Django messages framework are combined
        // with the level into a single string as notification.type
        const generalNotification = notifications.find(
          (notification: { type: string }) =>
            notification.type !== 'badge info',
        );
        const badgeNotification = notifications.find(
          (notification: { type: string }) =>
            notification.type === 'badge info',
        );

        if (generalNotification) {
          const tags: string[] = generalNotification.type.split(' ');
          setMessage({
            type: tags[tags.length - 1] as NotificationMessage['type'],
            content: generalNotification.content,
            duration: tags.includes('upload')
              ? UPLOAD_MESSAGE_DURATION
              : undefined,
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
