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

  return (
    <BadgeTooltipMessage.Provider value={message}>
      <ShowBadgeTooltip.Provider value={(tooltip) => setMessage(tooltip)}>
        {children}
      </ShowBadgeTooltip.Provider>
    </BadgeTooltipMessage.Provider>
  );
}
