import { createContext, useEffect, useState } from 'react';

type NotificationType =
  | 'debug'
  | 'error'
  | 'info'
  | 'success'
  | 'warning'
  | 'badge';

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
  const [message, setMessage] = useState<NotificationMessage | null>(null);

  // If there's a notification in the DOM set by Django, show it.
  // Note that we only show it once, and only when the UI has already
  // been rendered, to make sure users do see it.
  useEffect(() => {
    const rootElt = document.getElementById('root');
    if (rootElt?.dataset.notifications) {
      const notifications = JSON.parse(rootElt.dataset.notifications);
      if (notifications.length > 0) {
        // Our notification system only supports showing one notification
        // for the moment, so we only add the first notification here.
        setMessage(notifications[0]);
      }
    }
  }, []);

  return (
    <NotificationMessage.Provider value={message}>
      <ShowNotification.Provider value={setMessage}>
        {children}
      </ShowNotification.Provider>
    </NotificationMessage.Provider>
  );
}
