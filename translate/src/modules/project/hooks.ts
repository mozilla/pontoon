import { useAppSelector } from '../../../src/hooks';
import { PROJECT } from './reducer';

export const useProject = () => useAppSelector((state) => state[PROJECT]);
