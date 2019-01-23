/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './EntityDetails.css';

import { actions as lightboxActions } from 'core/lightbox';
import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as entitieslist from 'modules/entitieslist';
import * as history from 'modules/history';
import * as otherlocales from 'modules/otherlocales';
import { Editor } from 'modules/editor';

import { selectors } from '..';
import { suggest } from '../actions';
import Metadata from './Metadata';
import Tools from './Tools';

import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { DbEntity } from 'modules/entitieslist';
import type { HistoryState } from 'modules/history';
import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    activeTranslation: string,
    history: HistoryState,
    locale: ?Locale,
    otherlocales: LocalesState,
    parameters: NavigationParams,
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
    componentDidMount() {
        this.fetchHelpersData();
    }

    componentDidUpdate(prevProps: InternalProps) {
        const { parameters, pluralForm } = this.props;

        if (
            parameters.entity !== prevProps.parameters.entity ||
            pluralForm !== prevProps.pluralForm
        ) {
            this.fetchHelpersData();
        }
    }

    fetchHelpersData() {
        const { dispatch, parameters, pluralForm } = this.props;

        dispatch(history.actions.get(parameters.entity, parameters.locale, pluralForm));
        dispatch(otherlocales.actions.get(parameters.entity, parameters.locale));
    }

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
                locale={ state.locale }
                pluralForm= { state.pluralForm }
                sendSuggestion={ this.sendSuggestion }
            />
            <Tools
                parameters={ state.parameters }
                history={ state.history }
                otherlocales={ state.otherlocales }
            />
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslation: selectors.getTranslationForSelectedEntity(state),
        history: state[history.NAME],
        locale: locales.selectors.getCurrentLocaleData(state),
        otherlocales: state[otherlocales.NAME],
        parameters: navigation.selectors.getNavigationParams(state),
        pluralForm: plural.selectors.getPluralForm(state),
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
    };
};

export default connect(mapStateToProps)(EntityDetailsBase);
