import { createContext } from 'react';
import { useNotifications } from '../../src/hooks/useNotifications';

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
