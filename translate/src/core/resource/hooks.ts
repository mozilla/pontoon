import { useAppSelector } from '~/hooks';
import { RESOURCE } from './reducer';

export const useResource = () => useAppSelector((state) => state[RESOURCE]);
