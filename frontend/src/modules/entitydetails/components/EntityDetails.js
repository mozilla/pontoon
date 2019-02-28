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
import EntityNavigation from './EntityNavigation';
import Metadata from './Metadata';
import Tools from './Tools';

import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { DbEntity } from 'modules/entitieslist';
import type { HistoryState } from 'modules/history';
import type { MachineryState } from 'modules/machinery';
import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    activeTranslation: string,
    history: HistoryState,
    locale: ?Locale,
    machinery: MachineryState,
    nextEntity: DbEntity,
    previousEntity: DbEntity,
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
    constructor(props: InternalProps) {
        super(props);
        this.state = {
            translation: this.props.activeTranslation,
        };
    }

    componentDidMount() {
        this.fetchHelpersData();
    }

    componentDidUpdate(prevProps: InternalProps) {
        const { parameters, pluralForm, selectedEntity, activeTranslation } = this.props;

        if (
            parameters.entity !== prevProps.parameters.entity ||
            pluralForm !== prevProps.pluralForm ||
            selectedEntity !== prevProps.selectedEntity
        ) {
            this.updateEditorTranslation(activeTranslation);
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

    goToNextEntity = () => {
        const { router, nextEntity } = this.props;

        this.props.dispatch(
            navigation.actions.updateEntity(
                router,
                nextEntity.pk.toString(),
            )
        );
    }

    goToPreviousEntity = () => {
        const { router, previousEntity } = this.props;

        this.props.dispatch(
            navigation.actions.updateEntity(
                router,
                previousEntity.pk.toString(),
            )
        );
    }

    openLightbox = (image: string) => {
        this.props.dispatch(lightbox.actions.open(image));
    }

    updateEditorTranslation = (translation: string) => {
        this.setState({
            translation,
        });
    }

    sendTranslation = () => {
        const state = this.props;

        if (!state.selectedEntity || !state.locale) {
            return;
        }

        this.props.dispatch(actions.sendTranslation(
            state.selectedEntity.pk,
            this.state.translation,
            state.locale.code,
            state.selectedEntity.original,
            state.pluralForm,
            state.user.settings.forceSuggestions,
            state.nextEntity,
            state.router,
        ));
    }

    deleteTranslation = (translationId: number) => {
        const { parameters, pluralForm, dispatch } = this.props;
        dispatch(history.actions.deleteTranslation(
            parameters.entity,
            parameters.locale,
            pluralForm,
            translationId,
        ));
    }

    updateTranslationStatus = (translationId: number, change: string) => {
        const { nextEntity, parameters, pluralForm, router, dispatch } = this.props;
        dispatch(history.actions.updateStatus(
            change,
            parameters.entity,
            parameters.locale,
            parameters.resource,
            pluralForm,
            translationId,
            nextEntity,
            router,
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
            <EntityNavigation
                goToNextEntity={ this.goToNextEntity }
                goToPreviousEntity={ this.goToPreviousEntity }
            />
            <Metadata
                entity={ state.selectedEntity }
                locale={ state.locale }
                pluralForm={ state.pluralForm }
                openLightbox={ this.openLightbox }
            />
            <Editor
                translation={ this.state.translation }
                entity={ state.selectedEntity }
                locale={ state.locale }
                pluralForm= { state.pluralForm }
                user={ state.user }
                sendTranslation={ this.sendTranslation }
                updateEditorTranslation={ this.updateEditorTranslation }
                updateSetting={ this.updateSetting }
            />
            <Tools
                history={ state.history }
                locale={ state.locale }
                machinery={ state.machinery }
                otherlocales={ state.otherlocales }
                orderedOtherLocales={ state.orderedOtherLocales }
                preferredCount={ state.preferredCount }
                parameters={ state.parameters }
                user={ state.user }
                deleteTranslation={ this.deleteTranslation }
                updateTranslationStatus={ this.updateTranslationStatus }
                updateEditorTranslation={ this.updateEditorTranslation }
            />
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslation: selectors.getTranslationForSelectedEntity(state),
        history: state[history.NAME],
        locale: locales.selectors.getCurrentLocaleData(state),
        machinery: state[machinery.NAME],
        nextEntity: entitieslist.selectors.getNextEntity(state),
        previousEntity: entitieslist.selectors.getPreviousEntity(state),
        otherlocales: state[otherlocales.NAME],
        orderedOtherLocales: otherlocales.selectors.getOrderedOtherLocales(state),
        preferredCount: otherlocales.selectors.getPreferredLocalesCount(state),
        parameters: navigation.selectors.getNavigationParams(state),
        pluralForm: plural.selectors.getPluralForm(state),
        router: state.router,
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        user: state[user.NAME],
    };
};

export default connect(mapStateToProps)(EntityDetailsBase);
