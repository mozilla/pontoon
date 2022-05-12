import { useAppSelector } from '~/hooks';
import { PROJECT } from './reducer';

export const useProject = () => useAppSelector((state) => state[PROJECT]);
