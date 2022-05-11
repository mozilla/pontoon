import { useContext } from 'react';

import type { Entity } from '~/api/entity';
import { Location } from '~/context/location';
import { useAppSelector } from '~/hooks';

import { ENTITIES } from './reducer';

export const useEntities = () => useAppSelector((state) => state[ENTITIES]);

/** Return the currently selected Entity object.  */
export function useSelectedEntity(): Entity | undefined {
  const pk = useContext(Location).entity;
  return useAppSelector((state) =>
    state[ENTITIES].entities.find((entity) => entity.pk === pk),
  );
}

/** Next entity, or `null` if no next entity is available */
export function useNextEntity(): Entity | null {
  const pk = useContext(Location).entity;
  const entities = useAppSelector((state) => state[ENTITIES].entities);
  const curr = entities.findIndex((entity) => entity.pk === pk);
  if (curr === -1 || entities.length < 2) {
    return null;
  }
  const next = (curr + 1) % entities.length;
  return entities[next];
}

/** Previous entity, or `null` if no previous entity is available */
export function usePreviousEntity(): Entity | null {
  const pk = useContext(Location).entity;
  const entities = useAppSelector((state) => state[ENTITIES].entities);
  const curr = entities.findIndex((entity) => entity.pk === pk);
  if (curr === -1 || entities.length < 2) {
    return null;
  }
  const prev = (curr - 1 + entities.length) % entities.length;
  return entities[prev];
}
