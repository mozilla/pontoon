export { default as actions } from './actions';
export { default as reducer } from './reducer';


export { default as CommentCount } from './components/CommentCount';
export { default as CommentsList } from './components/CommentsList';

export type { TeamCommentState } from './reducer';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'commentslist';
