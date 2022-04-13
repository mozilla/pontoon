import { useContext } from 'react';

import { Location } from '~/context/location';
import type { Entity } from '~/core/api';
import { useAppSelector } from '~/hooks';
import { NAME as ENTITIES } from './index';

/** Return the currently selected Entity object.  */
export function useSelectedEntity(): Entity | undefined {
  const pk = useContext(Location).entity;
  return useAppSelector((state) =>
    state[ENTITIES].entities.find((entity) => entity.pk === pk),
  );
}

export function useNextEntity(): Entity | undefined {
  const pk = useContext(Location).entity;
  const entities = useAppSelector((state) => state[ENTITIES].entities);
  const curr = entities.findIndex((entity) => entity.pk === pk);
  if (curr === -1) return undefined;
  const next = (curr + 1) % entities.length;
  return entities[next];
}

export function usePreviousEntity(): Entity | undefined {
  const pk = useContext(Location).entity;
  const entities = useAppSelector((state) => state[ENTITIES].entities);
  const curr = entities.findIndex((entity) => entity.pk === pk);
  if (curr === -1) return undefined;
  const prev = (curr - 1 + entities.length) % entities.length;
  return entities[prev];
}
