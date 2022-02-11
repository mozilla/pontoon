import React, { useRef, useEffect } from 'react';
import useInfiniteScroll from 'react-infinite-scroll-hook';
import './EntitiesList.css';

import { AppStore, useAppDispatch, useAppSelector, useAppStore } from 'hooks';
import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as locale from 'core/locale';
import * as navigation from 'core/navigation';
import * as notification from 'core/notification';
import * as user from 'core/user';
import * as batchactions from 'modules/batchactions';
import * as unsavedchanges from 'modules/unsavedchanges';

import Entity from './Entity';
import { SkeletonLoader } from 'core/loaders';

import type { AppDispatch } from 'store';
import type { BatchActionsState } from 'modules/batchactions';
import type { Entity as EntityType } from 'core/api';
import type { EntitiesState } from 'core/entities';
import type { Locale } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import { usePrevious } from 'hooks/usePrevious';

type Props = {
    batchactions: BatchActionsState;
    entities: EntitiesState;
    isReadOnlyEditor: boolean;
    isTranslator: boolean;
    locale: Locale;
    parameters: NavigationParams;
    router: Record<string, any>;
};

type InternalProps = Props & {
    dispatch: AppDispatch;
    store: AppStore;
};

/**
 * Displays a list of entities and their current translation.
 *
 * This component will fetch entities when loaded, then display those
 * entities. It interacts with `core/navigation` when an entity is selected.
 *
 */
export const EntitiesListBase: React.FC<InternalProps> = (
    props,
): null | React.ReactElement<'div'> => {
    const list = useRef<any>();
    const isFirstRendered = useRef<boolean>(true);
    const prevProps = usePrevious(props);

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
    } = props.parameters;

    useEffect(() => {
        document.addEventListener('keydown', handleShortcuts);

        return () => {
            document.removeEventListener('keydown', handleShortcuts);
        };
    }, []);

    useEffect(() => {
        //a workaround preventing the first rendering
        if (isFirstRendered.current) {
            isFirstRendered.current = false;
        } else {
            props.dispatch(entities.actions.reset());

            // Scroll to selected entity when entity changes
            // and when entity list loads for the first time
            if (
                prevProps.parameters.entity ||
                (!prevProps.entities.entities.length &&
                    props.entities.entities.length)
            ) {
                const element = list.current.querySelector('li.selected');
                const mediaQuery = window.matchMedia(
                    '(prefers-reduced-motion: reduce)',
                );
                const behavior = mediaQuery.matches ? 'auto' : 'smooth';
                if (element) {
                    element.scrollIntoView({
                        behavior: behavior,
                        block: 'nearest',
                    });
                }
            }
        }
    }, [locale, project, resource, search, status, extra, tag, author, time]);

    const handleShortcuts: (event: KeyboardEvent) => void = (
        event: KeyboardEvent,
    ) => {
        const key = event.code;

        // On Ctrl + Shift + A, select all entities for batch editing.
        if (key === '65' && !event.altKey && event.ctrlKey && event.shiftKey) {
            event.preventDefault();

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
            } = props.parameters;

            props.dispatch(
                batchactions.actions.selectAll(
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

    const getSiblingEntities = (entity: number): void => {
        const { dispatch, locale } = props;
        dispatch(entities.actions.getSiblingEntities(entity, locale.code));
    };

    const toggleForBatchEditing = (
        entity: number,
        shiftKeyPressed: boolean,
    ): void => {
        const { dispatch } = props;

        const state = props.store.getState();
        const unsavedChangesExist = state[unsavedchanges.NAME].exist;
        const unsavedChangesIgnored = state[unsavedchanges.NAME].ignored;

        dispatch(
            unsavedchanges.actions.check(
                unsavedChangesExist,
                unsavedChangesIgnored,
                () => {
                    // If holding Shift, check all entities in the entity list between the
                    // lastCheckedEntity and the entity if entity not checked. If entity
                    // checked, uncheck all entities in-between.
                    const lastCheckedEntity =
                        props.batchactions.lastCheckedEntity;

                    if (shiftKeyPressed && lastCheckedEntity) {
                        const entityListIds = props.entities.entities.map(
                            (e) => e.pk,
                        );
                        const start = entityListIds.indexOf(entity);
                        const end = entityListIds.indexOf(lastCheckedEntity);

                        const entitySelection = entityListIds.slice(
                            Math.min(start, end),
                            Math.max(start, end) + 1,
                        );

                        if (props.batchactions.entities.includes(entity)) {
                            dispatch(
                                batchactions.actions.uncheckSelection(
                                    entitySelection,
                                    entity,
                                ),
                            );
                        } else {
                            dispatch(
                                batchactions.actions.checkSelection(
                                    entitySelection,
                                    entity,
                                ),
                            );
                        }
                    } else {
                        dispatch(batchactions.actions.toggleSelection(entity));
                    }
                },
            ),
        );
    };

    const selectEntity = (
        entity: EntityType,
        replaceHistory?: boolean,
    ): void => {
        const { dispatch, router } = props;

        const state = props.store.getState();
        const unsavedChangesExist = state[unsavedchanges.NAME].exist;
        const unsavedChangesIgnored = state[unsavedchanges.NAME].ignored;

        dispatch(
            unsavedchanges.actions.check(
                unsavedChangesExist,
                unsavedChangesIgnored,
                () => {
                    dispatch(batchactions.actions.resetSelection());
                    dispatch(editor.actions.reset());
                    dispatch(
                        navigation.actions.updateEntity(
                            router,
                            entity.pk.toString(),
                            replaceHistory,
                        ),
                    );
                },
            ),
        );
    };

    /*
     * If entity not provided through a URL parameter, or if provided entity
     * cannot be found, select the first entity in the list.
     */
    (function selectFirstEntityIfNoneSelected() {
        const selectedEntity = props.parameters.entity;
        const firstEntity = props.entities.entities[0];

        const entityIds = props.entities.entities.map((entity) => entity.pk);
        const isSelectedEntityValid = entityIds.indexOf(selectedEntity) > -1;

        if ((!selectedEntity || !isSelectedEntityValid) && firstEntity) {
            selectEntity(
                firstEntity,
                true, // Replace the last history item instead of pushing a new one.
            );

            // Only do this the very first time entities are loaded.
            if (
                props.entities.fetchCount === 1 &&
                selectedEntity &&
                !isSelectedEntityValid
            ) {
                props.dispatch(
                    notification.actions.add(
                        notification.messages.ENTITY_NOT_FOUND,
                    ),
                );
            }
        }
    })();

    const getMoreEntities = (): void => {
        const { dispatch } = props;

        const {
            locale,
            project,
            resource,
            entity,
            search,
            status,
            extra,
            tag,
            author,
            time,
        } = props.parameters;

        // Do not return a specific list of entities defined by their IDs.
        const entityIds: number[] = null;

        // Currently shown entities should be excluded from the next results.
        const currentEntityIds = props.entities.entities.map(
            (entity) => entity.pk,
        );

        dispatch(
            entities.actions.get(
                locale,
                project,
                resource,
                entityIds,
                currentEntityIds,
                entity.toString(),
                search,
                status,
                extra,
                tag,
                author,
                time,
            ),
        );
    };

    // InfiniteScroll will display information about loading during the request
    const hasMore = props.entities.fetching || props.entities.hasMore;
    const [sentryRef, { rootRef }] = useInfiniteScroll({
        loading: props.entities.fetching,
        hasNextPage: hasMore,
        onLoadMore: getMoreEntities,
        rootMargin: '0px 0px 400px 0px',
    });

    return (
        <div className='entities unselectable' ref={rootRef}>
            {hasMore || props.entities.entities.length ? (
                <ul>
                    {props.entities.entities.map((entity) => {
                        const selected =
                            !props.batchactions.entities.length &&
                            entity.pk === props.parameters.entity;

                        return (
                            <Entity
                                checkedForBatchEditing={props.batchactions.entities.includes(
                                    entity.pk,
                                )}
                                toggleForBatchEditing={toggleForBatchEditing}
                                entity={entity}
                                isReadOnlyEditor={props.isReadOnlyEditor}
                                isTranslator={props.isTranslator}
                                locale={props.locale}
                                selected={selected}
                                selectEntity={selectEntity}
                                key={entity.pk}
                                getSiblingEntities={getSiblingEntities}
                                parameters={props.parameters}
                            />
                        );
                    })}
                </ul>
            ) : (
                // When there are no results for the current search.
                <h3 className='no-results'>
                    <div className='fa fa-exclamation-circle'></div>
                    No results
                </h3>
            )}

            {hasMore && (
                <div ref={sentryRef}>
                    <SkeletonLoader key={0} items={props.entities.entities} />
                </div>
            )}
        </div>
    );
};

export default function EntitiesList(): React.ReactElement<
    typeof EntitiesListBase
> {
    const state = {
        batchactions: useAppSelector((state) => state[batchactions.NAME]),
        entities: useAppSelector((state) => state[entities.NAME]),
        isReadOnlyEditor: useAppSelector((state) =>
            entities.selectors.isReadOnlyEditor(state),
        ),
        isTranslator: useAppSelector((state) =>
            user.selectors.isTranslator(state),
        ),
        parameters: useAppSelector((state) =>
            navigation.selectors.getNavigationParams(state),
        ),
        locale: useAppSelector((state) => state[locale.NAME]),
        router: useAppSelector((state) => state.router),
    };

    return (
        <EntitiesListBase
            {...state}
            dispatch={useAppDispatch()}
            store={useAppStore()}
        />
    );
}
