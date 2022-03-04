import type { LocaleType } from '~/context/locale';
import type { LocationType } from '~/context/location';
import type { AppDispatch } from '~/store';

export const RESET: 'plural/RESET' = 'plural/RESET';
export const SELECT: 'plural/SELECT' = 'plural/SELECT';

/**
 * Move to next Entity or pluralForm.
 */
export function moveToNextTranslation(
  dispatch: AppDispatch,
  location: LocationType,
  entity: number,
  nextEntity: number,
  pluralForm: number,
  { cldrPlurals }: LocaleType,
): void {
  if (pluralForm !== -1 && pluralForm < cldrPlurals.length - 1) {
    dispatch(select(pluralForm + 1));
  } else if (nextEntity !== entity) {
    location.push({ entity: nextEntity });
  }
}

export type ResetAction = {
  type: typeof RESET;
};
export function reset(): ResetAction {
  return {
    type: RESET,
  };
}

export type SelectAction = {
  type: typeof SELECT;
  pluralForm: number;
};
export function select(pluralForm: number): SelectAction {
  return {
    type: SELECT,
    pluralForm,
  };
}

export default {
  moveToNextTranslation,
  reset,
  select,
};
