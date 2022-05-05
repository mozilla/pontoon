import { useAppSelector } from '~/hooks';
import { NAME } from './reducer';

export const useUnsavedChanges = () => useAppSelector((state) => state[NAME]);
