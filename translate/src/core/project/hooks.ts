import { useAppSelector } from '~/hooks';
import { NAME } from './reducer';

export const useProject = () => useAppSelector((state) => state[NAME]);
