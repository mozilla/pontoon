/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import { suggest } from '../actions';

import * as entitieslist from 'modules/entitieslist';
import { selectors as navSelectors } from 'core/navigation';

import Editor from './Editor';
import Metadata from './Metadata';

import type { DbEntity } from 'modules/entitieslist';
import type { Navigation } from 'core/navigation';


type Props = {|
    activeTranslation: string,
    navigation: Navigation,
    selectedEntity: ?DbEntity,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

type State = {|
    translation: string,
|};


/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export class EntityDetailsBase extends React.Component<InternalProps, State> {
    sendSuggestion = (translation: string): void => {
        const { navigation, selectedEntity } = this.props;

        if (!selectedEntity) {
            return;
        }

        this.props.dispatch(suggest(
            selectedEntity.pk,
            translation,
            navigation.locale,
            selectedEntity.original,
        ));
    }

    render(): React.Node {
        const { activeTranslation, navigation, selectedEntity } = this.props;

        if (!selectedEntity) {
            return <section className="entity-details">Select an entity</section>;
        }

        return <section className="entity-details">
            <Metadata entity={ selectedEntity } locale={ navigation.locale } />
            <Editor
                activeTranslation={ activeTranslation}
                selectedEntity={ selectedEntity }
                sendSuggestion={ this.sendSuggestion }
            />
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslation: entitieslist.selectors.getTranslationForSelectedEntity(state),
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        navigation: navSelectors.getNavigation(state),
    };
};

export default connect(mapStateToProps)(EntityDetailsBase);
