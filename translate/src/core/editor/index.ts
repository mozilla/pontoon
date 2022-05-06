export { EditorMenu } from './components/EditorMenu';
export { EditorSettings } from './components/EditorSettings';
export { FailedChecks } from './components/FailedChecks';
export { KeyboardShortcuts } from './components/KeyboardShortcuts';
export { TranslationLength } from './components/TranslationLength';

export { useAddTextToTranslation } from './hooks/useAddTextToTranslation';
export { useClearEditor } from './hooks/useClearEditor';
export { useCopyMachineryTranslation } from './hooks/useCopyMachineryTranslation';
export { useCopyOriginalIntoEditor } from './hooks/useCopyOriginalIntoEditor';
export { useCopyOtherLocaleTranslation } from './hooks/useCopyOtherLocaleTranslation';
export { useHandleShortcuts } from './hooks/useHandleShortcuts';
export { useSendTranslation } from './hooks/useSendTranslation';
export { useReplaceSelectionContent } from './hooks/useReplaceSelectionContent';
export { useUpdateTranslation } from './hooks/useUpdateTranslation';
export { useUpdateTranslationStatus } from './hooks/useUpdateTranslationStatus';
export { useUpdateUnsavedChanges } from './hooks/useUpdateUnsavedChanges';

export { EDITOR } from './reducer';
export type { EditorState } from './reducer';
export type { Translation } from './actions';
