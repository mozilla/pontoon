import { useContext } from 'react';

import type { Entity } from '~/api/entity';
import { EntityView } from '~/context/EntityView';
import { HistoryData } from '~/context/HistoryData';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import { useAppSelector } from '~/hooks';

import { ENTITIES } from './reducer';

export const useEntities = () => useAppSelector((state) => state[ENTITIES]);

/** Next entity, or `null` if no next entity is available */
export function useNextEntity(): Entity | null {
  const entities = useAppSelector((state) => state[ENTITIES].entities);
  const { entity } = useContext(EntityView);

  const curr = entities.indexOf(entity);
  if (curr === -1 || entities.length < 2) {
    return null;
  }

  const next = (curr + 1) % entities.length;
  return entities[next];
}

/** Previous entity, or `null` if no previous entity is available */
export function usePreviousEntity(): Entity | null {
  const entities = useAppSelector((state) => state[ENTITIES].entities);
  const { entity } = useContext(EntityView);

  const curr = entities.indexOf(entity);
  if (curr === -1 || entities.length < 2) {
    return null;
  }

  const prev = (curr - 1 + entities.length) % entities.length;
  return entities[prev];
}

export function usePushNextTranslatable() {
  const { push } = useContext(Location);
  const { cldrPlurals } = useContext(Locale);
  const { updateHistory } = useContext(HistoryData);
  const nextEntity = useNextEntity();
  const { entity, hasPluralForms, pluralForm, setPluralForm } =
    useContext(EntityView);

  return () => {
    if (hasPluralForms && pluralForm < cldrPlurals.length - 1) {
      setPluralForm(pluralForm + 1);
    } else if (nextEntity && nextEntity.pk !== entity.pk) {
      push({ entity: nextEntity.pk });
    } else {
      // No next string, so staying with current one -> history needs a refresh
      updateHistory();
    }
  };
}
