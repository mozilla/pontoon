import React, { createContext, useMemo, useState } from 'react';
import { fetchUsersList, MentionUser } from '~/api/user';

type MentionUsers = {
  /**
   * Fetch list of users for @-mentions.
   *
   * May be called multiple times, but data will only be fetched once.
   */
  initMentions(locale: string, projectId: number): void;
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
  const [state, setState] = useState<{
    projectId: number | undefined;
    mentionUsers: MentionUser[];
  }>(() => {
    return {
      projectId: undefined,
      mentionUsers: [],
    };
  });

  const initMentions = useMemo(
    () => (locale: string, projectId: number) => {
      if (state.projectId === projectId && state.mentionUsers.length > 0) {
        return;
      }
      fetchUsersList(locale, projectId).then((list) => {
        if (Array.isArray(list)) {
          setState({ projectId, mentionUsers: list });
        }
      });
    },
    [],
  );

  const value = useMemo(
    () => ({ initMentions, mentionUsers: state.mentionUsers }),
    [initMentions, state.mentionUsers],
  );
  return (
    <MentionUsers.Provider value={value}>{children}</MentionUsers.Provider>
  );
}
