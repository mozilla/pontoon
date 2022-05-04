import { useAppSelector } from '~/hooks';
import { NAME as BATCHACTIONS } from './reducer';

export const useBatchactions = () =>
  useAppSelector((state) => state[BATCHACTIONS]);
