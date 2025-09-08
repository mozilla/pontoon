import { useContext } from 'react';

import { EntityView } from '~/context/EntityView';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';

export function useReadonlyEditor(): boolean {
  const { entity } = useContext(EntityView);
  const isAuth = useAppSelector((state) => state[USER].isAuthenticated);
  return entity.readonly || !isAuth;
}
