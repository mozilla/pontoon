import { createContext, useContext } from 'react';
import { BadgeTooltipMessage, ShowBadgeTooltip } from './Notification';

export function BadgeTooltipProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const badgeMessage = useContext(BadgeTooltipMessage);
  const setBadgeMessage = useContext(ShowBadgeTooltip);

  return (
    <BadgeTooltipMessage.Provider value={badgeMessage}>
      <ShowBadgeTooltip.Provider value={setBadgeMessage}>
        {children}
      </ShowBadgeTooltip.Provider>
    </BadgeTooltipMessage.Provider>
  );
}
