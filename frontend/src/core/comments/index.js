/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';

export { default as AddComment } from './components/AddComment';
export { default as Comment } from './components/Comment';
export { default as CommentsList } from './components/CommentsList';

export type { CommentState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'comments';
