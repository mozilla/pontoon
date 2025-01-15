import React, { createContext } from 'react';
import { useNotifications } from '../hooks/useNotification';

type NotificationType = 'debug' | 'error' | 'info' | 'success' | 'warning';

export type NotificationMessage = Readonly<{
  type: NotificationType;
  content: string | React.ReactElement;
}>;

export const NotificationMessage = createContext<NotificationMessage | null>(
  null,
);

export const ShowNotification = createContext<
  (message: NotificationMessage | null) => void
>(() => {});

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

export function NotificationProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const { message, setMessage, badgeMessage, setBadgeMessage } =
    useNotifications();

  return (
    <NotificationMessage.Provider value={message}>
      <ShowNotification.Provider value={setMessage}>
        <BadgeTooltipMessage.Provider value={badgeMessage}>
          <ShowBadgeTooltip.Provider value={setBadgeMessage}>
            {children}
          </ShowBadgeTooltip.Provider>
        </BadgeTooltipMessage.Provider>
      </ShowNotification.Provider>
    </NotificationMessage.Provider>
  );
}
