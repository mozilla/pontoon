import type { SourceType } from '~/api/machinery';

import {
  Action,
  Translation,
  END_UPDATE_TRANSLATION,
  RESET_SELECTION,
  RESET_EDITOR,
  SET_INITIAL_TRANSLATION,
  START_UPDATE_TRANSLATION,
  UPDATE,
  UPDATE_SELECTION,
  UPDATE_MACHINERY_SOURCES,
} from './actions';

// Name of this module.
// Used as the key to store this module's reducer.
export const EDITOR = 'editor';

export type EditorState = {
  readonly translation: Translation;
  // Used for storing the initial translation in Fluent editor,
  // needed for detecting unsaved changes.
  readonly initialTranslation: Translation;

  // Source of the current change: 'internal' if from inside the Editor,
  // 'history', 'machinery', 'otherlocales' if copied from corresponding
  // Helper tab, 'external' otherwise. This allows the Editor to behave
  // differently depending on the type of change.
  readonly changeSource: string;

  readonly machinerySources: Array<SourceType>;

  readonly machineryTranslation: string;

  // Order to replace the currently selected text inside the Editor with
  // this content. This is reset after that change has been made. Because
  // we have different Editor implementations, we need to let those components
  // perform the actual replacement logic.
  readonly selectionReplacementContent: string;

  // True when there is a request to send a new translation running, false
  // otherwise. Used to prevent duplicate actions from users spamming their
  // keyboard or mouse.
  readonly isRunningRequest: boolean;
};

const initial: EditorState = {
  translation: '',
  initialTranslation: '',
  changeSource: 'reset',
  machinerySources: [],
  machineryTranslation: '',
  selectionReplacementContent: '',
  isRunningRequest: false,
};

export function reducer(
  state: EditorState = initial,
  action: Action,
): EditorState {
  switch (action.type) {
    case END_UPDATE_TRANSLATION:
      return {
        ...state,
        isRunningRequest: false,
      };
    case UPDATE:
      return {
        ...state,
        translation: action.translation,
        changeSource: action.changeSource,
      };
    case UPDATE_SELECTION:
      return {
        ...state,
        selectionReplacementContent: action.content,
        changeSource: action.changeSource,
      };
    case SET_INITIAL_TRANSLATION:
      return {
        ...state,
        initialTranslation: action.translation,
        machineryTranslation: '',
        machinerySources: [],
      };
    case START_UPDATE_TRANSLATION:
      return {
        ...state,
        isRunningRequest: true,
      };
    case RESET_SELECTION:
      return {
        ...state,
        selectionReplacementContent: '',
        changeSource: 'internal',
      };
    case RESET_EDITOR:
      return {
        ...initial,
        isRunningRequest: state.isRunningRequest,
      };
    case UPDATE_MACHINERY_SOURCES:
      return {
        ...state,
        machineryTranslation: action.machineryTranslation,
        machinerySources: action.machinerySources,
      };
    default:
      return state;
  }
}
