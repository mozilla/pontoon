import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import type { Entity } from '~/api/entity';
import type { EntityTranslation } from '~/api/translation';
import { ENTITIES } from '~/core/entities/reducer';
import { useAppSelector } from '~/hooks';

import { Locale } from './Locale';
import { Location } from './Location';

const emptyEntity: Entity = {
  pk: 0,
  original: '',
  original_plural: '',
  machinery_original: '',
  comment: '',
  group_comment: '',
  resource_comment: '',
  key: '',
  context: '',
  format: '',
  path: '',
  project: {},
  source: [],
  translation: [],
  readonly: true,
  isSibling: false,
};

export type EntityView = {
  entity: Entity;
  hasPluralForms: boolean;
  pluralForm: number;
  setPluralForm(pluralForm: number): void;
};

const initEntityView: EntityView = {
  entity: emptyEntity,
  hasPluralForms: false,
  pluralForm: 0,
  setPluralForm: () => {},
};

export const EntityView = createContext(initEntityView);

export function EntityViewProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const pk = useContext(Location).entity;
  const pluralCount = useContext(Locale).cldrPlurals.length;
  const entities = useAppSelector((state) => state[ENTITIES].entities);

  const [state, setState] = useState(initEntityView);

  useEffect(() => {
    const entity = entities.find((entity) => entity.pk === pk) ?? emptyEntity;
    const hasPluralForms =
      pluralCount > 1 && !!entity.original_plural && entity.format !== 'ftl';

    const setPluralForm = hasPluralForms
      ? (next: number) => {
          const pluralForm =
            next >= pluralCount ? 0 : next < 0 ? pluralCount - 1 : next;
          setState((prev) => ({ ...prev, pluralForm }));
        }
      : () => {};

    setState({ entity, hasPluralForms, pluralForm: 0, setPluralForm });
  }, [pk, pluralCount, entities]);

  return <EntityView.Provider value={state}>{children}</EntityView.Provider>;
}

/**
 * Return the active translation for the given entity and current plural form.
 *
 * The active translation is either the approved one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export function useActiveTranslation(): EntityTranslation | null {
  const { entity, pluralForm } = useContext(EntityView);
  return useMemo(() => {
    const tx = entity.translation[pluralForm];
    return tx && !tx.rejected ? tx : null;
  }, [entity, pluralForm]);
}

export function useEntitySource(): string {
  const { entity, pluralForm } = useContext(EntityView);
  return useMemo(
    () => (pluralForm > 0 && entity.original_plural) || entity.original,
    [entity, pluralForm],
  );
}
