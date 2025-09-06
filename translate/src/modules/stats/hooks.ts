import { useAppSelector } from '../../../src/hooks';
import { STATS } from './reducer';

export const useStats = () => useAppSelector((state) => state[STATS]);
