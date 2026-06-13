import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import type { Entity } from '~/api/entity';
import type { EntityTranslation } from '~/api/translation';
import { ENTITIES } from '~/modules/entities/reducer';
import { useAppSelector } from '~/hooks';

import { Location } from './Location';
import { MessageEntry } from '~/utils/message';
import { messageEntryFromEntity } from '~/utils/message/fromEntity';

const emptyEntity: Entity = {
  pk: 0,
  key: [],
  format: '',
  original: '',
  value: [],
  comment: '',
  date_created: '',
  path: '',
  project: {},
  readonly: true,
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
    return tx && tx.status !== 'rejected' ? tx : null;
  }, [entity]);
}

export function useEntityEntry(): MessageEntry {
  const { entity } = useContext(EntityView);
  return useMemo(() => messageEntryFromEntity(entity), [entity]);
}
