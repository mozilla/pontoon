import { useContext } from 'react';

import { EntityView } from '../../src/context/EntityView';
import { USER } from '../../src/modules/user';
import { useAppSelector } from '../../src/hooks';

export function useReadonlyEditor(): boolean {
  const { entity } = useContext(EntityView);
  const isAuth = useAppSelector((state) => state[USER].isAuthenticated);
  return entity.readonly || !isAuth;
}
