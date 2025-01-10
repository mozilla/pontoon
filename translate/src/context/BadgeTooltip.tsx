import { createContext, useEffect, useState } from 'react';
import { Localized } from '@fluent/react';

export type BadgeTooltipMessage = Readonly<{
  badgeName: string | null;
  badgeLevel: number | null;
}>;

export const BadgeTooltipMessage = createContext<BadgeTooltipMessage | null>(
  null,
);

export const ShowBadgeTooltip = createContext<
  (tooltip: BadgeTooltipMessage | null) => void
>(() => {});

export function BadgeTooltipProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const [message, setMessage] = useState<BadgeTooltipMessage | null>(null);

  useEffect(() => {
    const rootElt = document.getElementById('root');
    if (rootElt?.dataset.notifications) {
      const notifications = JSON.parse(rootElt.dataset.notifications);
      if (notifications.length > 0) {
        const parsed = notifications.map(
          (notification: { content: string; type: string }) => {
            if (notification.type === 'info') {
              // Badge update information
              return JSON.parse(notification.content);
            } else {
              return { content: notification.content, type: notification.type };
            }
          },
        );
        setMessage(parsed[1]);
      }
    }
  }, []);

  return (
    <BadgeTooltipMessage.Provider value={message}>
      <ShowBadgeTooltip.Provider value={(tooltip) => setMessage(tooltip)}>
        {children}
      </ShowBadgeTooltip.Provider>
    </BadgeTooltipMessage.Provider>
  );
}
