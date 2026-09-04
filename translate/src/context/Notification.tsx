import { createContext } from 'react';
import { useNotifications } from '~/hooks/useNotifications';

type NotificationType = 'debug' | 'error' | 'info' | 'success' | 'warning';

export type NotificationMessage = Readonly<{
  type: NotificationType;
  content: string | React.ReactElement;
  /** How long to show the message, in milliseconds. */
  duration?: number;
}>;

export const NotificationMessage = createContext<NotificationMessage | null>(
  null,
);

export const ShowNotification = createContext<
  (message: NotificationMessage | null) => void
>(() => {});

export function NotificationProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const { message, setMessage } = useNotifications();

  return (
    <NotificationMessage.Provider value={message}>
      <ShowNotification.Provider value={setMessage}>
        {children}
      </ShowNotification.Provider>
    </NotificationMessage.Provider>
  );
}
