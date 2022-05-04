import React, { useCallback, useContext, useEffect, useRef } from 'react';
import useInfiniteScroll from 'react-infinite-scroll-hook';

import { Locale } from '~/context/locale';
import { Location } from '~/context/location';
import type { Entity as EntityType } from '~/core/api';
import { reset as resetEditor } from '~/core/editor/actions';
import {
  fetchEntities,
  fetchSiblingEntities,
  resetEntities,
} from '~/core/entities/actions';
import { useEntities } from '~/core/entities/hooks';
import { SkeletonLoader } from '~/core/loaders';
import { addNotification } from '~/core/notification/actions';
import notificationMessages from '~/core/notification/messages';
import { useAppDispatch, useAppStore } from '~/hooks';
import { usePrevious } from '~/hooks/usePrevious';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import {
  checkSelection,
  resetSelection,
  selectAll,
  toggleSelection,
  uncheckSelection,
} from '~/modules/batchactions/actions';
import { useBatchactions } from '~/modules/batchactions/hooks';
import { NAME as UNSAVEDCHANGES } from '~/modules/unsavedchanges';
import { check as checkUnsavedChanges } from '~/modules/unsavedchanges/actions';

import './EntitiesList.css';
import { Entity } from './Entity';

/**
 * Displays a list of entities and their current translation.
 *
 * This component will fetch entities when loaded, then display those
 * entities. It interacts with `core/navigation` when an entity is selected.
 *
 */
export function EntitiesList(): React.ReactElement<'div'> {
  const dispatch = useAppDispatch();
  const store = useAppStore();

  const batchactions = useBatchactions();
  const { entities, fetchCount, fetching, hasMore } = useEntities();
  const isReadOnlyEditor = useReadonlyEditor();
  const parameters = useContext(Location);

  const mounted = useRef(false);
  const list = useRef<HTMLDivElement>(null);

  const {
    locale,
    project,
    resource,
    search,
    status,
    extra,
    tag,
    author,
    time,
  } = parameters;

  useEffect(() => {
    const handleShortcuts = (ev: KeyboardEvent) => {
      // On Ctrl + Shift + A, select all entities for batch editing.
      if (ev.keyCode === 65 && !ev.altKey && ev.ctrlKey && ev.shiftKey) {
        ev.preventDefault();
        dispatch(
          selectAll(
            locale,
            project,
            resource,
            search,
            status,
            extra,
            tag,
            author,
            time,
          ),
        );
      }
    };
    document.addEventListener('keydown', handleShortcuts);
    return () => document.removeEventListener('keydown', handleShortcuts);
  }, [dispatch, parameters]);

  const selectEntity = useCallback(
    (entity: EntityType, replaceHistory?: boolean) => {
      // Do not re-select already selected entity
      if (entity.pk !== parameters.entity) {
        const state = store.getState();
        const { exist, ignored } = state[UNSAVEDCHANGES];

        dispatch(
          checkUnsavedChanges(exist, ignored, () => {
            dispatch(resetSelection());
            dispatch(resetEditor());
            const nextLocation = { entity: entity.pk };
            if (replaceHistory) {
              parameters.replace(nextLocation);
            } else {
              parameters.push(nextLocation);
            }
          }),
        );
      }
    },
    [dispatch, parameters, store],
  );

  /*
   * If entity not provided through a URL parameter, or if provided entity
   * cannot be found, select the first entity in the list.
   */
  useEffect(() => {
    const selectedEntity = parameters.entity;
    const firstEntity = entities[0];
    const isValid = entities.some(({ pk }) => pk === selectedEntity);

    if ((!selectedEntity || !isValid) && firstEntity) {
      // Replace the last history item instead of pushing a new one.
      selectEntity(firstEntity, true);

      // Only do this the very first time entities are loaded.
      if (fetchCount === 1 && selectedEntity && !isValid) {
        dispatch(addNotification(notificationMessages.ENTITY_NOT_FOUND));
      }
    }
  });

  // Whenever the route changes, we want to verify that the user didn't
  // change locale, project, resource... If they did, then we'll have
  // to reset the current list of entities, in order to start a fresh
  // list and hide the previous entities.
  //
  // Notes:
  //  * It might seem to be an anti-pattern to change the state after the
  //    component has rendered, but that's actually the easiest way to
  //    implement that feature.
  //  * Other solutions might involve using `history.listen` to trigger
  //    an action on each location change.
  //  * I haven't been able to figure out how to test this feature. It
  //    is possible that going for another possible solutions will make
  //    testing easier, which would be very desirable.
  useEffect(() => {
    if (mounted.current) {
      dispatch(resetEntities());
    }
  }, [
    dispatch,
    // Note: entity is explicitly not included here
    locale,
    project,
    resource,
    search,
    status,
    extra,
    tag,
    author,
    time,
  ]);

  const scrollToSelected = useCallback(() => {
    if (!mounted.current) {
      return;
    }
    const element = list.current?.querySelector('li.selected');
    const mediaQuery = window.matchMedia?.('(prefers-reduced-motion: reduce)');
    element?.scrollIntoView?.({
      behavior: mediaQuery?.matches ? 'auto' : 'smooth',
      block: 'nearest',
    });
  }, []);

  // Scroll to selected entity when entity changes
  // and when entity list loads for the first time
  const prevEntityCount = usePrevious(entities.length);
  useEffect(() => {
    if (!prevEntityCount && entities.length > 0) {
      scrollToSelected();
    }
  }, [entities.length]);
  useEffect(scrollToSelected, [parameters.entity]);

  const { code } = useContext(Locale);
  const getSiblingEntities = useCallback(
    (entity: number) => dispatch(fetchSiblingEntities(entity, code)),
    [dispatch, code],
  );

  const toggleForBatchEditing = useCallback(
    (entity: number, shiftKeyPressed: boolean) => {
      const state = store.getState();
      const { exist, ignored } = state[UNSAVEDCHANGES];

      dispatch(
        checkUnsavedChanges(exist, ignored, () => {
          // If holding Shift, check all entities in the entity list between the
          // lastCheckedEntity and the entity if entity not checked. If entity
          // checked, uncheck all entities in-between.
          if (shiftKeyPressed && batchactions.lastCheckedEntity) {
            const entityListIds = entities.map((e) => e.pk);
            const start = entityListIds.indexOf(entity);
            const end = entityListIds.indexOf(batchactions.lastCheckedEntity);

            const entitySelection = entityListIds.slice(
              Math.min(start, end),
              Math.max(start, end) + 1,
            );

            if (batchactions.entities.includes(entity)) {
              dispatch(uncheckSelection(entitySelection, entity));
            } else {
              dispatch(checkSelection(entitySelection, entity));
            }
          } else {
            dispatch(toggleSelection(entity));
          }
        }),
      );
    },
    [batchactions, dispatch, entities, store],
  );

  const getMoreEntities = useCallback(() => {
    if (!fetching) {
      dispatch(
        fetchEntities(
          locale,
          project,
          resource,
          null, // Do not return a specific list of entities defined by their IDs.
          entities.map((entity) => entity.pk), // Currently shown entities should be excluded from the next results.
          parameters.entity.toString(),
          search,
          status,
          extra,
          tag,
          author,
          time,
        ),
      );
    }
  }, [dispatch, entities, fetching, parameters]);

  // Must be after other useEffect() calls, as they are run in order during mount
  useEffect(() => {
    mounted.current = true;
  }, []);

  const hasNextPage = fetching || hasMore;

  const [sentryRef, { rootRef }] = useInfiniteScroll({
    loading: fetching,
    hasNextPage,
    onLoadMore: getMoreEntities,
    rootMargin: '0px 0px 600px 0px',
  });
  useEffect(() => {
    rootRef(list.current);
  }, [list.current]);

  if (entities.length === 0 && !hasNextPage) {
    // When there are no results for the current search.
    return (
      <div className='entities unselectable' ref={list}>
        <h3 className='no-results'>
          <div className='fa fa-exclamation-circle'></div>
          No results
        </h3>
      </div>
    );
  }

  return (
    <div className='entities unselectable' ref={list}>
      <ul>
        {entities.map((entity) => (
          <Entity
            key={entity.pk}
            checkedForBatchEditing={batchactions.entities.includes(entity.pk)}
            toggleForBatchEditing={toggleForBatchEditing}
            entity={entity}
            isReadOnlyEditor={isReadOnlyEditor}
            selected={
              !batchactions.entities.length && entity.pk === parameters.entity
            }
            selectEntity={selectEntity}
            getSiblingEntities={getSiblingEntities}
            parameters={parameters}
          />
        ))}
      </ul>
      {hasNextPage && <SkeletonLoader items={entities} sentryRef={sentryRef} />}
    </div>
  );
}
