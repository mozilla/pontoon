import { useContext } from 'react';

import type { Entity } from '~/api/entity';
import { EntityView } from '~/context/EntityView';
import { HistoryData } from '~/context/HistoryData';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import { useAppSelector } from '~/hooks';

import { ENTITIES } from './reducer';

export const useEntities = () => useAppSelector((state) => state[ENTITIES]);

export function usePushNextTranslatable() {
  const { push } = useContext(Location);
  const { updateHistory } = useContext(HistoryData);
  const entities = useAppSelector((state) => state[ENTITIES].entities);
  const { entity } = useContext(EntityView);

  const curr = entities.indexOf(entity);
  let nextEntity = null;
  if (curr === -1 || entities.length < 2) {
  } else {
    const next = (curr + 1) % entities.length;
    nextEntity = entities[next];
  }

  return () => {
    if (nextEntity && nextEntity.pk !== entity.pk) {
      push({ entity: nextEntity.pk });
    } else {
      // No next string, so staying with current one -> history needs a refresh
      updateHistory();
    }
  };
}
