/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './EntityDetails.css';

import { actions as lightboxActions } from 'core/lightbox';
import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';

import * as entitieslist from 'modules/entitieslist';
import { NAME as HISTORY_NAME } from 'modules/history';

import { suggest } from '../actions';
import { selectors } from '..';
import { suggest } from '../actions';
import Editor from './Editor';
import Metadata from './Metadata';
import Tools from './Tools';

import type { Locale } from 'core/locales';
import type { Navigation } from 'core/navigation';
import type { DbEntity } from 'modules/entitieslist';
import type { HistoryState } from 'modules/history';


type Props = {|
    activeTranslation: string,
    history: HistoryState,
    locale: ?Locale,
    navigation: Navigation,
    pluralForm: number,
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
            state.pluralForm,
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

        const historyCount = state.history.translations.length;

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
            <Tools
                historyCount={ historyCount }
            />
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslation: selectors.getTranslationForSelectedEntity(state),
        history: state[HISTORY_NAME],
        locale: locales.selectors.getCurrentLocaleData(state),
        navigation: navigation.selectors.getNavigation(state),
        pluralForm: plural.selectors.getPluralForm(state),
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
    };
};

export default connect(mapStateToProps)(EntityDetailsBase);
