import { useAppSelector } from '~/hooks';
import { STATS } from './reducer';

export const useStats = () => useAppSelector((state) => state[STATS]);
