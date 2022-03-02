import type { Location } from '~/hooks/useLocation';
export type NavigationParams = Location;

export { default as actions } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME = 'navigation';
