/* @flow */

export { default as actions } from './actions';
export { default as reducer } from './reducer';
export { default as selectors } from './selectors';

export { default as EditorMenu } from './components/EditorMenu';
export { default as EditorSettings } from './components/EditorSettings';
export { default as FailedChecks } from './components/FailedChecks';
export { default as KeyboardShortcuts } from './components/KeyboardShortcuts';
export { default as TranslationLength } from './components/TranslationLength';

export { default as useAddTextToTranslation } from './hooks/useAddTextToTranslation';
export { default as useClearEditor } from './hooks/useClearEditor';
export { default as useCopyMachineryTranslation } from './hooks/useCopyMachineryTranslation';
export { default as useCopyOriginalIntoEditor } from './hooks/useCopyOriginalIntoEditor';
export { default as useCopyOtherLocaleTranslation } from './hooks/useCopyOtherLocaleTranslation';
export { default as useHandleShortcuts } from './hooks/useHandleShortcuts';
export { default as useLoadTranslation } from './hooks/useLoadTranslation';
export { default as useSendTranslation } from './hooks/useSendTranslation';
export { default as useReplaceSelectionContent } from './hooks/useReplaceSelectionContent';
export { default as useUpdateTranslation } from './hooks/useUpdateTranslation';
export { default as useUpdateTranslationStatus } from './hooks/useUpdateTranslationStatus';
export { default as useUpdateUnsavedChanges } from './hooks/useUpdateUnsavedChanges';

export type { EditorState } from './reducer';
export type { Translation } from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const NAME: string = 'editor';
