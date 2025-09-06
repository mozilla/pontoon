import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import type { Entity } from '../../src/api/entity';
import type { EntityTranslation } from '../../src/api/translation';
import { ENTITIES } from '../../src/modules/entities/reducer';
import { useAppSelector } from '../../src/hooks';

import { Locale } from './Locale';
import { Location } from './Location';

const emptyEntity: Entity = {
  pk: 0,
  key: [],
  original: '',
  machinery_original: '',
  comment: '',
  group_comment: '',
  resource_comment: '',
  meta: [],
  format: '',
  path: '',
  project: {},
  translation: undefined,
  readonly: true,
  isSibling: false,
  date_created: '',
};

export type EntityView = { entity: Entity };

const initEntityView: EntityView = { entity: emptyEntity };

export const EntityView = createContext(initEntityView);

export function EntityViewProvider({
  children,
}: {
  children: React.ReactElement;
}) {
  const pk = useContext(Location).entity;
  const entities = useAppSelector((state) => state[ENTITIES].entities);

  const entity = entities.find((entity) => entity.pk === pk) ?? emptyEntity;

  const [state, setState] = useState<EntityView>({ entity });

  useEffect(() => setState((prev) => ({ ...prev, entity })), [entity]);

  useEffect(() => {
    setState((prev) => ({ entity: prev.entity }));
  }, [pk, entity.format]);

  return <EntityView.Provider value={state}>{children}</EntityView.Provider>;
}

/**
 * Return the active translation for the given entity.
 *
 * The active translation is either the approved one, the fuzzy one, or the
 * most recent non-rejected one.
 */
export function useActiveTranslation(): EntityTranslation | null {
  const { entity } = useContext(EntityView);
  return useMemo(() => {
    const tx = entity.translation;
    return tx && !tx.rejected ? tx : null;
  }, [entity]);
}
