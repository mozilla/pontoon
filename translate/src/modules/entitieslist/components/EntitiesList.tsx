import { Localized } from '@fluent/react';
import React, { useCallback, useContext, useEffect, useRef } from 'react';
import useInfiniteScroll from 'react-infinite-scroll-hook';

import type { Entity as EntityType } from '~/api/entity';
import { logUXAction } from '~/api/uxaction';
import { EntitiesList as EntitiesListContext } from '~/context/EntitiesList';
import { Locale } from '~/context/Locale';
import { Location } from '~/context/Location';
import {
  getEntities,
  getSiblingEntities,
  resetEntities,
} from '~/modules/entities/actions';
import { useEntities } from '~/modules/entities/hooks';
import { SkeletonLoader } from '~/modules/loaders';
import { ENTITY_NOT_FOUND } from '~/modules/notification/messages';
import { useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import { useWindowWidth } from '~/hooks/useWindowWidth';
import { usePrevious } from '~/hooks/usePrevious';
import {
  checkSelection,
  resetSelection,
  selectAll,
  toggleSelection,
  uncheckSelection,
} from '~/modules/batchactions/actions';
import { useBatchactions } from '~/modules/batchactions/hooks';
import { UnsavedActions } from '~/context/UnsavedChanges';

import './EntitiesList.css';
import { Entity } from './Entity';
import { USER } from '~/modules/user';
import { ShowNotification } from '~/context/Notification';

const EntitiesToolbar = ({
  count,
  onEdit,
  onClear,
}: {
  count: number;
  onEdit: () => void;
  onClear: () => void;
}) => (
  <div className='toolbar clearfix'>
    <Localized
      id='entitieslist-EntitiesList--clear-selected'
      attrs={{ title: true }}
      elems={{
        glyph: <i className='fas fa-times fa-lg' />,
      }}
    >
      <button
        title='Uncheck selected strings'
        onClick={onClear}
        className='clear-selected'
      >
        {'<glyph></glyph> CLEAR'}
      </button>
    </Localized>
    <Localized
      id='entitieslist-EntitiesList--edit-selected'
      attrs={{ title: true }}
      elems={{
        glyph: <i className='fas fa-chevron-right fa-lg' />,
        stress: <span className='selected-count' />,
      }}
      vars={{ count }}
    >
      <button
        title='Edit Selected Strings'
        onClick={onEdit}
        className='edit-selected'
      >
        {'EDIT <stress>{ $count }</stress> STRINGS<glyph></glyph>'}
      </button>
    </Localized>
  </div>
);

/**
 * Displays a list of entities and their current translation.
 *
 * This component will fetch entities when loaded,
 * then display those entities.
 */
export function EntitiesList(): React.ReactElement<'div'> {
  const dispatch = useAppDispatch();
  const store = useAppStore();

  const showNotification = useContext(ShowNotification);
  const batchactions = useBatchactions();
  const { entities, fetchCount, fetching, hasMore, page } = useEntities();
  const location = useContext(Location);
  const isAuthUser = useAppSelector((state) => state[USER].isAuthenticated);
  const { checkUnsavedChanges } = useContext(UnsavedActions);

  const mounted = useRef(false);
  const list = useRef<HTMLDivElement>(null);

  const selectedEntitiesCount = batchactions.entities.length;
  const windowWidth = useWindowWidth();
  const entitiesList = useContext(EntitiesListContext);
  const quitBatchActions = useCallback(() => dispatch(resetSelection()), []);
  const showBatchActions = useCallback(() => entitiesList.show(false), []);

  useEffect(() => {
    const handleShortcuts = (ev: KeyboardEvent) => {
      // On Ctrl + Shift + A, select all entities for batch editing.
      if (ev.keyCode === 65 && !ev.altKey && ev.ctrlKey && ev.shiftKey) {
        ev.preventDefault();
        dispatch(selectAll(location));
      }
    };
    document.addEventListener('keydown', handleShortcuts);
    return () => document.removeEventListener('keydown', handleShortcuts);
  }, [dispatch, location]);

  const selectEntity = useCallback(
    (entity: EntityType, replaceHistory?: boolean) => {
      // Do not re-select already selected entity
      if (entity.pk !== location.entity) {
        checkUnsavedChanges(() => {
          dispatch(resetSelection());
          const nextLocation = { entity: entity.pk };
          if (replaceHistory) {
            location.replace(nextLocation);
          } else {
            location.push(nextLocation);
          }
        });
      }
    },
    [dispatch, location, store],
  );

  /*
   * If entity not provided through a URL parameter, or if provided entity
   * cannot be found, select the first entity in the list.
   */
  useEffect(() => {
    const selectedEntity = location.entity;
    const firstEntity = entities[0];
    const isValid = entities.some(({ pk }) => pk === selectedEntity);

    if ((!selectedEntity || !isValid) && firstEntity) {
      // Replace the last history item instead of pushing a new one.
      selectEntity(firstEntity, true);

      // Only do this the very first time entities are loaded.
      if (fetchCount === 1 && selectedEntity && !isValid) {
        showNotification(ENTITY_NOT_FOUND);
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
    // Note: location.entity is explicitly not included here
    location.locale,
    location.project,
    location.resource,
    location.search,
    location.status,
    location.extra,
    location.tag,
    location.author,
    location.time,
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
  useEffect(scrollToSelected, [location.entity]);

  const { code } = useContext(Locale);
  const getSiblingEntities_ = useCallback(
    (entity: number) => dispatch(getSiblingEntities(entity, code)),
    [dispatch, code],
  );

  const toggleForBatchEditing = useCallback(
    (entity: number, shiftKeyPressed: boolean) => {
      checkUnsavedChanges(() => {
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
      });
    },
    [batchactions, dispatch, entities, store],
  );

  const getMoreEntities = useCallback(() => {
    if (!fetching) {
      // Currently shown entities should be excluded from the next results.
      dispatch(getEntities(location, page));
      if (isAuthUser) {
        logUXAction(
          'Load: String list with search parameter',
          'Search Options Statistics',
          {
            search_exclude_source_strings:
              location.search_exclude_source_strings,
            search_identifiers: location.search_identifiers,
            search_match_case: location.search_match_case,
            search_match_whole_word: location.search_match_whole_word,
            search_rejected_translations: location.search_rejected_translations,
          },
        );
      }
    }
  }, [dispatch, entities, fetching, isAuthUser, location, page]);

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
          <div className='fas fa-exclamation-circle'></div>
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
            isReadOnlyEditor={entity.readonly || !isAuthUser}
            selected={!selectedEntitiesCount && entity.pk === location.entity}
            selectEntity={selectEntity}
            getSiblingEntities={getSiblingEntities_}
            parameters={location}
          />
        ))}
      </ul>
      {hasNextPage && <SkeletonLoader items={entities} sentryRef={sentryRef} />}
      {selectedEntitiesCount === 0 || windowWidth !== 'narrow' ? null : (
        <EntitiesToolbar
          count={selectedEntitiesCount}
          onEdit={showBatchActions}
          onClear={quitBatchActions}
        />
      )}
    </div>
  );
}
