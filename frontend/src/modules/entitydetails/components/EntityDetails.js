/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './EntityDetails.css';

import api from 'core/api';
import * as lightbox from 'core/lightbox';
import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as user from 'core/user';
import * as entitieslist from 'modules/entitieslist';
import * as history from 'modules/history';
import * as machinery from 'modules/machinery';
import * as otherlocales from 'modules/otherlocales';
import * as editor from 'modules/editor';

import { selectors } from '..';
import EntityNavigation from './EntityNavigation';
import Metadata from './Metadata';
import Helpers from './Helpers';

import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { EditorState } from 'modules/editor';
import type { DbEntity } from 'modules/entitieslist';
import type { ChangeOperation, HistoryState } from 'modules/history';
import type { MachineryState } from 'modules/machinery';
import type { LocalesState } from 'modules/otherlocales';


type Props = {|
    activeTranslation: string,
    editor: EditorState,
    history: HistoryState,
    isReadOnlyEditor: boolean,
    isTranslator: boolean,
    locale: Locale,
    machinery: MachineryState,
    nextEntity: DbEntity,
    previousEntity: DbEntity,
    otherlocales: LocalesState,
    orderedOtherLocales: Array<api.types.OtherLocaleTranslation>,
    preferredLocalesCount: number,
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
        this.updateEditorTranslation(this.props.activeTranslation);
        this.updateFailedChecks();
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
            this.updateFailedChecks();
            this.fetchHelpersData();
        }
    }

    fetchHelpersData() {
        const { dispatch, locale, parameters, pluralForm, selectedEntity } = this.props;

        if (!parameters.entity || !selectedEntity || !locale) {
            return;
        }

        dispatch(history.actions.get(parameters.entity, parameters.locale, pluralForm));
        dispatch(machinery.actions.get(selectedEntity.original, locale, selectedEntity.pk));
        dispatch(otherlocales.actions.get(parameters.entity, parameters.locale));
    }

    updateFailedChecks() {
        const { dispatch, pluralForm, selectedEntity } = this.props;

        if (!selectedEntity) {
            return;
        }

        const plural = pluralForm === -1 ? 0 : pluralForm;
        const translation = selectedEntity.translation[plural];

        // Only show failed checks for active translations that are approved or fuzzy,
        // i.e. when their status icon is colored as error/warning in the string list
        if (
            translation &&
            (translation.errors.length || translation.warnings.length) &&
            (translation.approved || translation.fuzzy)
        ) {
            const failedChecks = {
                clErrors: translation.errors,
                clWarnings: translation.warnings,
                pErrors: [],
                pndbWarnings: [],
                ttWarnings: [],
            };
            dispatch(editor.actions.updateFailedChecks(failedChecks, 'stored'));
        } else {
            dispatch(editor.actions.resetFailedChecks());
        }
    }

    searchMachinery = (query: string) => {
        const { dispatch, locale, selectedEntity } = this.props;

        let source = query;
        let pk = null;

        // On empty query, use source string as input
        if (selectedEntity && !query.length) {
            source = selectedEntity.original;
            pk = selectedEntity.pk;
        }

        dispatch(machinery.actions.get(source, locale, pk));
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
        this.props.dispatch(editor.actions.update(translation, 'external'));
    }

    addTextToEditorTranslation = (content: string) => {
        this.props.dispatch(editor.actions.updateSelection(content));
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

    /*
     * This is a copy of EditorBase.updateTranslationStatus().
     * When changing this function, you probably want to change both.
     * We might want to refactor to keep the logic in one place only.
     */
    updateTranslationStatus = (translationId: number, change: ChangeOperation) => {
        const { locale, nextEntity, parameters, pluralForm, router, dispatch } = this.props;
        dispatch(history.actions.updateStatus(
            change,
            parameters.entity,
            locale,
            parameters.resource,
            pluralForm,
            translationId,
            nextEntity,
            router,
        ));
    }

    render() {
        const state = this.props;

        if (!state.locale) {
            return null;
        }

        if (!state.selectedEntity) {
            return <section className="entity-details"></section>;
        }

        return <section className="entity-details">
            <EntityNavigation
                goToNextEntity={ this.goToNextEntity }
                goToPreviousEntity={ this.goToPreviousEntity }
            />
            <Metadata
                entity={ state.selectedEntity }
                isReadOnlyEditor={ state.isReadOnlyEditor }
                locale={ state.locale }
                pluralForm={ state.pluralForm }
                openLightbox={ this.openLightbox }
                addTextToEditorTranslation={ this.addTextToEditorTranslation }
            />
            <editor.Editor />
            <Helpers
                history={ state.history }
                isReadOnlyEditor={ state.isReadOnlyEditor }
                isTranslator={ state.isTranslator }
                locale={ state.locale }
                machinery={ state.machinery }
                otherlocales={ state.otherlocales }
                orderedOtherLocales={ state.orderedOtherLocales }
                preferredLocalesCount={ state.preferredLocalesCount }
                parameters={ state.parameters }
                user={ state.user }
                deleteTranslation={ this.deleteTranslation }
                updateTranslationStatus={ this.updateTranslationStatus }
                updateEditorTranslation={ this.updateEditorTranslation }
                searchMachinery={ this.searchMachinery }
            />
        </section>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslation: selectors.getTranslationForSelectedEntity(state),
        editor: state[editor.NAME],
        history: state[history.NAME],
        isReadOnlyEditor: selectors.isReadOnlyEditor(state),
        isTranslator: user.selectors.isTranslator(state),
        locale: locales.selectors.getCurrentLocaleData(state),
        machinery: state[machinery.NAME],
        nextEntity: entitieslist.selectors.getNextEntity(state),
        previousEntity: entitieslist.selectors.getPreviousEntity(state),
        otherlocales: state[otherlocales.NAME],
        orderedOtherLocales: otherlocales.selectors.getOrderedOtherLocales(state),
        preferredLocalesCount: otherlocales.selectors.getPreferredLocalesCount(state),
        parameters: navigation.selectors.getNavigationParams(state),
        pluralForm: plural.selectors.getPluralForm(state),
        router: state.router,
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        user: state[user.NAME],
    };
};

export default connect(mapStateToProps)(EntityDetailsBase);
