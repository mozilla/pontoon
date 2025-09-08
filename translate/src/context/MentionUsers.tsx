import React, { createContext, useMemo, useState } from 'react';
import { fetchUsersList, MentionUser } from '~/api/user';

type MentionUsers = {
  /**
   * Fetch list of users for @-mentions.
   *
   * May be called multiple times, but data will only be fetched once.
   */
  initMentions(): void;
  mentionUsers: MentionUser[];
};

export const MentionUsers = createContext<MentionUsers>({
  initMentions: () => {},
  mentionUsers: [],
});

export function MentionUsersProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const [mentionUsers, setUsers] = useState<MentionUser[]>([]);
  const [initMentions, setInit] = useState(() => () => {
    setInit(() => () => {});
    fetchUsersList().then((list) => {
      if (Array.isArray(list)) {
        setUsers(list);
      }
    });
  });
  const value = useMemo(
    () => ({ initMentions, mentionUsers }),
    [initMentions, mentionUsers],
  );
  return (
    <MentionUsers.Provider value={value}>{children}</MentionUsers.Provider>
  );
}
