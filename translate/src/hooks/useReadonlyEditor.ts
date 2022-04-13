import { useSelectedEntity } from '~/core/entities/hooks';
import { NAME as USER } from '~/core/user';
import { useAppSelector } from '~/hooks';

export function useReadonlyEditor(): boolean {
  const entity = useSelectedEntity();
  const isAuth = useAppSelector((state) => state[USER].isAuthenticated);
  return entity?.readonly || !isAuth;
}
