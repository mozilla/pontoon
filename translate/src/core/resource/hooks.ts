import { useAppSelector } from '~/hooks';
import { NAME } from './reducer';

export const useResource = () => useAppSelector((state) => state[NAME]);
