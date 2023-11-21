import { useAppSelector } from '~/hooks';
import { ENTITIESLIST } from './reducer';

export const useEntitiesList = () =>
  useAppSelector((state) => state[ENTITIESLIST]);
