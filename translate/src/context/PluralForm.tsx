import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import type { Entity } from '~/api/entity';
import type { EntityTranslation } from '~/api/translation';

import { Location } from './Location';

export type PluralForm = {
  pluralForm: number;
  setPluralForm(pluralForm: number): void;
};

export const PluralForm = createContext<PluralForm>({
  pluralForm: -1,
  setPluralForm: () => {},
});

export function PluralFormProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const [pluralForm, setPluralForm] = useState(-1);

  useEffect(() => setPluralForm(-1), [useContext(Location)]);

  const state = useMemo(() => ({ pluralForm, setPluralForm }), [pluralForm]);
  return <PluralForm.Provider value={state}>{children}</PluralForm.Provider>;
}

/**
 * Return the plural form to use for the given entity.
 *
 * If the entity has a plural form, and the current plural form is -1,
 * this will correctly return 0 instead of -1. In all other cases, return
 * the plural form as stored in the state.
 */
export function usePluralForm(entity: Entity | undefined): PluralForm {
  let { pluralForm, setPluralForm } = useContext(PluralForm);
  if (pluralForm === -1 && entity?.original_plural) {
    pluralForm = 0;
  }
  return { pluralForm, setPluralForm };
}

/**
 * Return the active translation for the given entity and current plural form.
 *
 * The active translation is either the approved one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export function useTranslationForEntity(
  entity: Entity | undefined,
): EntityTranslation | undefined {
  let { pluralForm } = useContext(PluralForm);
  if (pluralForm === -1) {
    pluralForm = 0;
  }
  const tx = entity?.translation[pluralForm];
  return tx && !tx.rejected ? tx : undefined;
}
