import * as React from 'react';
import { useDispatch, useSelector, useStore } from 'react-redux';
import InfiniteScroll from 'react-infinite-scroller';

import './EntitiesList.css';

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

import type { BatchActionsState } from 'modules/batchactions';
import type { Entity as EntityType } from 'core/api';
import type { EntitiesState } from 'core/entities';
import type { Locale } from 'core/locale';
import type { NavigationParams } from 'core/navigation';

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
    dispatch: (...args: Array<any>) => any;
    store: Record<string, any>;
};

/**
 * Displays a list of entities and their current translation.
 *
 * This component will fetch entities when loaded, then display those
 * entities. It interacts with `core/navigation` when an entity is selected.
 *
 */
export class EntitiesListBase extends React.Component<InternalProps> {
    list: { current: any };

    constructor(props: InternalProps) {
        super(props);
        this.list = React.createRef();
    }

    componentDidMount() {
        document.addEventListener('keydown', this.handleShortcuts);

        this.selectFirstEntityIfNoneSelected();
    }

    componentWillUnmount() {
        document.removeEventListener('keydown', this.handleShortcuts);
    }

    componentDidUpdate(prevProps: InternalProps) {
        this.selectFirstEntityIfNoneSelected();

        // Whenever the route changes, we want to verify that the user didn't
        // change locale, project, resource... If they did, then we'll have
        // to reset the current list of entities, in order to start a fresh
        // list and hide the previous entities.
        //
        // Notes:
        //  * It might seem to be an anti-pattern to change the state after the
        //    component has rendered, but that's actually the easiest way to
        //    implement that feature. Note that the first render is not shown
        //    to the user, so there should be no blinking here.
        //    Cf. https://reactjs.org/docs/react-component.html#componentdidupdate
        //  * Other solutions might involve using `connected-react-router`'s
        //    redux actions (see https://stackoverflow.com/a/37911318/1462501)
        //    or using `history.listen` to trigger an action on each location
        //    change.
        //  * I haven't been able to figure out how to test this feature. It
        //    is possible that going for another possible solutions will make
        //    testing easier, which would be very desirable.
        const previous = prevProps.parameters;
        const current = this.props.parameters;
        if (
            previous.locale !== current.locale ||
            previous.project !== current.project ||
            previous.resource !== current.resource ||
            previous.search !== current.search ||
            previous.status !== current.status ||
            previous.extra !== current.extra ||
            previous.tag !== current.tag ||
            previous.author !== current.author ||
            previous.time !== current.time
        ) {
            this.props.dispatch(entities.actions.reset());
        }

        // Scroll to selected entity when entity changes
        // and when entity list loads for the first time
        if (
            previous.entity !== current.entity ||
            (!prevProps.entities.entities.length &&
                this.props.entities.entities.length)
        ) {
            const list = this.list.current;
            const element = list.querySelector('li.selected');

            if (element) {
                element.scrollIntoView({
                    behavior: 'smooth',
                    block: 'nearest',
                });
            }
        }
    }

    handleShortcuts: (event: KeyboardEvent) => void = (
        event: KeyboardEvent,
    ) => {
        const key = event.keyCode;

        // On Ctrl + Shift + A, select all entities for batch editing.
        if (key === 65 && !event.altKey && event.ctrlKey && event.shiftKey) {
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
            } = this.props.parameters;

            this.props.dispatch(
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

    /*
     * If entity not provided through a URL parameter, or if provided entity
     * cannot be found, select the first entity in the list.
     */
    selectFirstEntityIfNoneSelected() {
        const props = this.props;
        const selectedEntity = props.parameters.entity;
        const firstEntity = props.entities.entities[0];

        const entityIds = props.entities.entities.map((entity) => entity.pk);
        const isSelectedEntityValid = entityIds.indexOf(selectedEntity) > -1;

        if ((!selectedEntity || !isSelectedEntityValid) && firstEntity) {
            this.selectEntity(
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
    }

    selectEntity: (entity: EntityType, replaceHistory?: boolean) => void = (
        entity: EntityType,
        replaceHistory?: boolean,
    ) => {
        const { dispatch, router } = this.props;

        const state = this.props.store.getState();
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

    toggleForBatchEditing: (
        entity: number,
        shiftKeyPressed: boolean,
    ) => void = (entity: number, shiftKeyPressed: boolean) => {
        const props = this.props;
        const { dispatch } = props;

        const state = this.props.store.getState();
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

    getMoreEntities: () => void = () => {
        const props = this.props;
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

        // Temporary fix for the infinite number of requests from InfiniteScroller
        // More info at:
        // * https://github.com/CassetteRocks/react-infinite-scroller/issues/149
        // * https://github.com/CassetteRocks/react-infinite-scroller/issues/163
        if (props.entities.fetching) {
            return;
        }

        // Do not return a specific list of entities defined by their IDs.
        const entityIds = null;

        // Currently shown entities should be excluded from the next results.
        const currentEntityIds = props.entities.entities.map(
            (entity) => entity.pk,
        );

        props.dispatch(
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

    render(): React.ReactElement<'div'> {
        const props = this.props;
        const search = props.parameters.search;

        // InfiniteScroll will display information about loading during the request
        const hasMore = props.entities.fetching || props.entities.hasMore;

        return (
            <div className='entities unselectable' ref={this.list}>
                <InfiniteScroll
                    pageStart={1}
                    loadMore={this.getMoreEntities}
                    hasMore={hasMore}
                    loader={
                        <SkeletonLoader
                            key={0}
                            items={props.entities.entities}
                        />
                    }
                    useWindow={false}
                    threshold={600}
                >
                    {hasMore || props.entities.entities.length ? (
                        <ul>
                            {props.entities.entities.map((entity, i) => {
                                const selected =
                                    !props.batchactions.entities.length &&
                                    entity.pk === props.parameters.entity;

                                return (
                                    <Entity
                                        checkedForBatchEditing={props.batchactions.entities.includes(
                                            entity.pk,
                                        )}
                                        toggleForBatchEditing={
                                            this.toggleForBatchEditing
                                        }
                                        entity={entity}
                                        isReadOnlyEditor={
                                            props.isReadOnlyEditor
                                        }
                                        isTranslator={props.isTranslator}
                                        locale={props.locale}
                                        search={search}
                                        selected={selected}
                                        selectEntity={this.selectEntity}
                                        key={i}
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
                </InfiniteScroll>
            </div>
        );
    }
}

export default function EntitiesList(): React.ReactElement<
    typeof EntitiesListBase
> {
    const state = {
        batchactions: useSelector((state) => state[batchactions.NAME]),
        entities: useSelector((state) => state[entities.NAME]),
        isReadOnlyEditor: useSelector((state) =>
            entities.selectors.isReadOnlyEditor(state),
        ),
        isTranslator: useSelector((state) =>
            user.selectors.isTranslator(state),
        ),
        parameters: useSelector((state) =>
            navigation.selectors.getNavigationParams(state),
        ),
        locale: useSelector((state) => state[locale.NAME]),
        router: useSelector((state) => state.router),
    };

    return (
        <EntitiesListBase
            {...state}
            dispatch={useDispatch()}
            store={useStore()}
        />
    );
}
