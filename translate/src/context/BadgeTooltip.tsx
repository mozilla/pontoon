import { createContext } from 'react';
import { useNotifications } from '../../src/hooks/useNotifications';

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
  const { badgeMessage, setBadgeMessage } = useNotifications();

  return (
    <BadgeTooltipMessage.Provider value={badgeMessage}>
      <ShowBadgeTooltip.Provider value={(tooltip) => setBadgeMessage(tooltip)}>
        {children}
      </ShowBadgeTooltip.Provider>
    </BadgeTooltipMessage.Provider>
  );
}
