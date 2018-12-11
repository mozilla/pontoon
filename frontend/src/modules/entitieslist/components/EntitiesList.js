/* @flow */

import React from 'react';
import { connect } from 'react-redux';
import InfiniteScroll from 'react-infinite-scroller';

import './EntitiesList.css';

import {
    actions as navActions,
    selectors as navSelectors,
} from 'core/navigation';
import type { Navigation } from 'core/navigation';

import { actions, NAME } from '..';
import Entity from './Entity';
import EntitiesLoader from './EntitiesLoader'

import type { Entities, DbEntity } from '../reducer';


type Props = {|
    entities: {|
        entities: Entities,
        hasMore: boolean,
        fetching: boolean,
    |},
    parameters: Navigation,
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
    componentDidUpdate(prevProps: InternalProps) {
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
    }

    selectEntity = (entity: DbEntity) => {
        this.props.dispatch(
            navActions.updateEntity(this.props.router, entity.pk.toString())
        );
    }

    getMoreEntities = () => {
        const { entities, parameters } = this.props;
        const { locale, project, resource, search, status } = parameters;

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
                search,
                status,
            )
        );
    }

    render() {
        const { entities } = this.props;
        const selectedEntity = this.props.parameters.entity;

        // InfiniteScroll will display information about loading during the request
        const hasMore = entities.fetching || entities.hasMore;

        return <div className="entities">
            <InfiniteScroll
                pageStart={ 1 }
                loadMore={ this.getMoreEntities }
                hasMore={ hasMore }
                loader={ <EntitiesLoader key={0} /> }
                useWindow={ false }
                threshold={ 600 }
            >
            { (hasMore || entities.entities.length) ?
                <ul>
                    { entities.entities.map((entity, i) => {
                        return <Entity
                            entity={ entity }
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
        parameters: navSelectors.getNavigation(state),
        router: state.router,
    };
};

export default connect(mapStateToProps)(EntitiesListBase);
