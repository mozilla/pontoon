/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import { suggest } from '../actions';

import { actions as lightboxActions } from 'core/lightbox';
import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as entitieslist from 'modules/entitieslist';
import { History } from 'modules/history';

import { selectors } from '..';
import Editor from './Editor';
import Metadata from './Metadata';

import type { DbEntity } from 'modules/entitieslist';
import type { Locale } from 'core/locales';
import type { Navigation } from 'core/navigation';


type Props = {|
    activeTranslation: string,
    navigation: Navigation,
    selectedEntity: ?DbEntity,
    pluralForm: number,
    locale: ?Locale,
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
    openLightbox = (image: string) => {
        this.props.dispatch(lightboxActions.open(image));
    }

    sendSuggestion = (translation: string) => {
        const state = this.props;

        if (!state.selectedEntity || !state.locale) {
            return;
        }

        this.props.dispatch(suggest(
            state.selectedEntity.pk,
            translation,
            state.locale.code,
            state.selectedEntity.original,
        ));
    }

    render() {
        const state = this.props;

        if (!state.locale) {
            return null;
        }

        if (!state.selectedEntity) {
            return <section className="entity-details">Select an entity</section>;
        }

        return <section className="entity-details">
            <Metadata
                entity={ state.selectedEntity }
                locale={ state.locale }
                pluralForm={ state.pluralForm }
                openLightbox={ this.openLightbox }
            />
            <Editor
                translation={ state.activeTranslation}
                entity={ state.selectedEntity }
                pluralForm= { state.pluralForm }
                sendSuggestion={ this.sendSuggestion }
            />
            <History />
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslation: selectors.getTranslationForSelectedEntity(state),
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        navigation: navigation.selectors.getNavigation(state),
        pluralForm: plural.selectors.getPluralForm(state),
        locale: locales.selectors.getCurrentLocaleData(state),
    };
};

export default connect(mapStateToProps)(EntityDetailsBase);
