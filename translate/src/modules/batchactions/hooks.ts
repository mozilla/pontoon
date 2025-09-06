import { useAppSelector } from '../../../src/hooks';
import { BATCHACTIONS } from './reducer';

export const useBatchactions = () =>
  useAppSelector((state) => state[BATCHACTIONS]);
