/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './EntityDetails.css';

import * as lightbox from 'core/lightbox';
import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as user from 'core/user';
import * as entitieslist from 'modules/entitieslist';
import * as history from 'modules/history';
import * as machinery from 'modules/machinery';
import * as otherlocales from 'modules/otherlocales';
import { Editor } from 'modules/editor';

import { actions, selectors } from '..';
import Metadata from './Metadata';
import Tools from './Tools';

import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { DbEntity } from 'modules/entitieslist';
import type { HistoryState } from 'modules/history';
import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    activeTranslation: string,
    history: HistoryState,
    locale: ?Locale,
    nextEntity: ?DbEntity,
    otherlocales: LocalesState,
    parameters: NavigationParams,
    pluralForm: number,
    router: Object,
    selectedEntity: ?DbEntity,
    user: UserState,
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
        const { parameters, pluralForm, selectedEntity } = this.props;

        if (
            parameters.entity !== prevProps.parameters.entity ||
            pluralForm !== prevProps.pluralForm ||
            selectedEntity !== prevProps.selectedEntity
        ) {
            this.fetchHelpersData();
        }
    }

    fetchHelpersData() {
        const { dispatch, locale, parameters, pluralForm, selectedEntity } = this.props;

        if (!parameters.entity || !selectedEntity || !locale) {
            return;
        }

        dispatch(history.actions.get(parameters.entity, parameters.locale, pluralForm));
        dispatch(machinery.actions.get(selectedEntity, locale));
        dispatch(otherlocales.actions.get(parameters.entity, parameters.locale));
    }

    openLightbox = (image: string) => {
        this.props.dispatch(lightbox.actions.open(image));
    }

    sendTranslation = (translation: string) => {
        const state = this.props;

        if (!state.selectedEntity || !state.locale) {
            return;
        }

        this.props.dispatch(actions.sendTranslation(
            state.selectedEntity.pk,
            translation,
            state.locale.code,
            state.selectedEntity.original,
            state.pluralForm,
            state.user.settings.forceSuggestions,
            state.nextEntity,
            state.router,
        ));
    }

    updateSetting = (setting: string, value: boolean) => {
        this.props.dispatch(user.actions.saveSetting(setting, value, this.props.user.username));
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
                settings={ state.user.settings }
                sendTranslation={ this.sendTranslation }
                updateSetting={ this.updateSetting }
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
        nextEntity: entitieslist.selectors.getNextEntity(state),
        otherlocales: state[otherlocales.NAME],
        parameters: navigation.selectors.getNavigationParams(state),
        pluralForm: plural.selectors.getPluralForm(state),
        router: state.router,
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        user: state[user.NAME],
    };
};

export default connect(mapStateToProps)(EntityDetailsBase);
