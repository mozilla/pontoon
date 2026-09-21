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
      const notifications = JSON.parse(rootElt.dataset.notifications);
      if (notifications.length > 0) {
        // Extra tags from the Django messages framework are combined
        // with the level into a single string as notification.type
        const tags: string[] = notifications[0].type.split(' ');
        setMessage({
          type: tags[tags.length - 1] as NotificationMessage['type'],
          content: notifications[0].content,
        });
      }
    }
  }, []);

  return { message, setMessage, badgeMessage, setBadgeMessage };
}
