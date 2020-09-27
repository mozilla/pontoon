/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';
export { default as selectors } from './selectors';

export { default as connectedEditor } from './components/connectedEditor';
export { default as EditorMenu } from './components/EditorMenu';
export { default as EditorSettings } from './components/EditorSettings';
export { default as FailedChecks } from './components/FailedChecks';
export { default as KeyboardShortcuts } from './components/KeyboardShortcuts';
export { default as TranslationLength } from './components/TranslationLength';

export type { EditorProps } from './components/connectedEditor';
export type { EditorState } from './reducer';
export type { Translation } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'editor';
