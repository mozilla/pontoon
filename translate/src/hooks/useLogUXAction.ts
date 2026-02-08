import { useAppSelector } from '~/hooks';
import { USER } from '~/modules/user';
import { logUXAction } from '../api/uxaction';

import { useCallback } from 'react';

export function useLogUXAction(): (
  action_type: string,
  experiment: string | null,
  data: Record<string, string | number | boolean> | null,
) => Promise<void> | void {
  const isAuthenticated = useAppSelector((state) =>
    Boolean(state[USER].isAuthenticated),
  );

  return useCallback(
    (action_type, experiment, data) => {
      if (!isAuthenticated) return;
      return logUXAction(action_type, experiment, data);
    },
    [isAuthenticated],
  );
}
