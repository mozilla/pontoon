import { useAppSelector } from '~/hooks';
import { NAME } from './reducer';

export const useStats = () => useAppSelector((state) => state[NAME]);
