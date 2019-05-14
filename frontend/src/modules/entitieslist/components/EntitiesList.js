/* @flow */

import React from 'react';
import { connect } from 'react-redux';
import InfiniteScroll from 'react-infinite-scroller';

import './EntitiesList.css';

import * as locales from 'core/locales';
import * as navigation from 'core/navigation';

import { actions, NAME } from '..';
import Entity from './Entity';
import { CircleLoader } from 'core/loaders'

import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { Entities, DbEntity } from '../reducer';


type Props = {|
    entities: {|
        entities: Entities,
        hasMore: boolean,
        fetching: boolean,
    |},
    locale: Locale,
    parameters: NavigationParams,
    router: Object,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

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
        this.selectFirstEntityIfNoneSelected();
    }

    componentDidUpdate(prevProps: InternalProps) {
        this.selectFirstEntityIfNoneSelected();

        // Whenever the route changes, we want to verify that the user didn't
        // change locale, project or resource. If they did, then we'll have
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
            previous.status !== current.status
        ) {
            this.props.dispatch(actions.reset());
        }

        if (previous.entity !== current.entity) {
            this.scrollToSelectedElement();
        }
    }

    scrollToSelectedElement() {
        const list = this.list.current;
        const element = list.querySelector('li.selected');

        if (!element) {
            return;
        }

        const listTop = list.scrollTop;
        const listHeight = list.clientHeight;
        const listBottom = listTop + listHeight;

        const elementTop = element.offsetTop;
        const elementHeight = element.offsetHeight;
        const elementBottom = elementTop + elementHeight;

        if (elementTop < listTop) {
            list.scrollTop = elementTop;
        }
        else if (elementBottom >= listBottom) {
            list.scrollTop = Math.max(elementBottom - listHeight, 0);
        }
    }

    selectFirstEntityIfNoneSelected() {
        const { entities, parameters, router } = this.props;
        const selectedEntity = parameters.entity;

        if (!selectedEntity && entities.entities.length > 0) {
            this.props.dispatch(
                navigation.actions.updateEntity(
                    router,
                    entities.entities[0].pk.toString(),
                )
            );
        }
    }

    selectEntity = (entity: DbEntity) => {
        this.props.dispatch(
            navigation.actions.updateEntity(this.props.router, entity.pk.toString())
        );
    }

    getMoreEntities = () => {
        const { entities, parameters } = this.props;
        const { locale, project, resource, entity, search, status } = parameters;

        // Temporary fix for the infinite number of requests from InfiniteScroller
        // More info at:
        // * https://github.com/CassetteRocks/react-infinite-scroller/issues/149
        // * https://github.com/CassetteRocks/react-infinite-scroller/issues/163
        if (entities.fetching) {
            return;
        }

        // Currently shown entities should be excluded from the next results.
        const currentEntityIds = entities.entities.map(entity => entity.pk);

        this.props.dispatch(
            actions.get(
                locale,
                project,
                resource,
                currentEntityIds,
                entity.toString(),
                search,
                status,
            )
        );
    }

    render() {
        const state = this.props;
        const selectedEntity = state.parameters.entity;

        // InfiniteScroll will display information about loading during the request
        const hasMore = state.entities.fetching || state.entities.hasMore;

        return <div
            className="entities"
            ref={ this.list }
        >
            <InfiniteScroll
                pageStart={ 1 }
                loadMore={ this.getMoreEntities }
                hasMore={ hasMore }
                loader={ <CircleLoader key={0} /> }
                useWindow={ false }
                threshold={ 600 }
            >
            { (hasMore || state.entities.entities.length) ?
                <ul>
                    { state.entities.entities.map((entity, i) => {
                        return <Entity
                            entity={ entity }
                            locale={ state.locale }
                            selectEntity={ this.selectEntity }
                            key={ i }
                            selected={ entity.pk === selectedEntity }
                        />;
                    }) }
                </ul>
                :
                // When there are no results for the current search.
                <h3 className="no-results">
                    <div className="fa fa-exclamation-circle"></div>
                    No results
                </h3>
            }
            </InfiniteScroll>
        </div>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        entities: state[NAME],
        parameters: navigation.selectors.getNavigationParams(state),
        locale: locales.selectors.getCurrentLocaleData(state),
        router: state.router,
    };
};

export default connect(mapStateToProps)(EntitiesListBase);
