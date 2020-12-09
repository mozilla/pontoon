/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { push } from 'connected-react-router';

import './EntityDetails.css';

import * as comments from 'core/comments';
import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as lightbox from 'core/lightbox';
import * as locale from 'core/locale';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as terms from 'core/term';
import * as user from 'core/user';
import * as utils from 'core/utils';
import * as history from 'modules/history';
import * as machinery from 'modules/machinery';
import * as otherlocales from 'modules/otherlocales';
import * as teamcomments from 'modules/teamcomments';
import * as unsavedchanges from 'modules/unsavedchanges';
import * as notification from 'core/notification';

import EditorSelector from './EditorSelector';
import EntityNavigation from './EntityNavigation';
import Metadata from './Metadata';
import Helpers from './Helpers';

import type { Entity, SourceType } from 'core/api';
import type { Locale } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import type { TermState } from 'core/term';
import type { UserState } from 'core/user';
import type { ChangeOperation, HistoryState } from 'modules/history';
import type { MachineryState } from 'modules/machinery';
import type { LocalesState } from 'modules/otherlocales';
import type { TeamCommentState } from 'modules/teamcomments';

type Props = {|
    activeTranslationString: string,
    history: HistoryState,
    isReadOnlyEditor: boolean,
    isTranslator: boolean,
    locale: Locale,
    machinery: MachineryState,
    nextEntity: Entity,
    previousEntity: Entity,
    otherlocales: LocalesState,
    teamComments: TeamCommentState,
    terms: TermState,
    parameters: NavigationParams,
    pluralForm: number,
    router: Object,
    selectedEntity: Entity,
    unsavedChangesExist: boolean,
    unsavedChangesIgnored: boolean,
    user: UserState,
    users: UserState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

type State = {|
    translation: string,
    commentTabIndex: number,
    contactPerson: string,
|};

/**
 * Component showing details about an entity.
 *
 * Shows the metadata of the entity and an editor for translations.
 */
export class EntityDetailsBase extends React.Component<InternalProps, State> {
    commentTabRef: { current: Object };
    constructor(props: InternalProps, state: State) {
        super(props);
        this.state = {
            ...state,
            commentTabIndex: 0,
            contactPerson: '',
        };
        this.commentTabRef = React.createRef();
    }
    componentDidMount() {
        this.updateFailedChecks();
        this.fetchHelpersData();
    }

    componentDidUpdate(prevProps: InternalProps) {
        const {
            activeTranslationString,
            nextEntity,
            pluralForm,
            selectedEntity,
        } = this.props;

        if (
            pluralForm !== prevProps.pluralForm ||
            selectedEntity !== prevProps.selectedEntity ||
            (selectedEntity === nextEntity &&
                activeTranslationString !== prevProps.activeTranslationString)
        ) {
            this.updateFailedChecks();
            this.fetchHelpersData();
        }
    }

    /*
     * Only fetch helpers data if the entity changes.
     * Also fetch history data if the pluralForm changes.
     */
    fetchHelpersData() {
        const {
            dispatch,
            locale,
            nextEntity,
            parameters,
            pluralForm,
            selectedEntity,
        } = this.props;

        if (!parameters.entity || !selectedEntity || !locale) {
            return;
        }

        if (
            selectedEntity.pk !== this.props.history.entity ||
            pluralForm !== this.props.history.pluralForm ||
            selectedEntity === nextEntity
        ) {
            dispatch(history.actions.request(parameters.entity, pluralForm));
            dispatch(
                history.actions.get(
                    parameters.entity,
                    parameters.locale,
                    pluralForm,
                ),
            );
        }

        const source = utils.getOptimizedContent(
            selectedEntity.machinery_original,
            selectedEntity.format,
        );

        if (
            source !== this.props.terms.sourceString &&
            parameters.project !== 'terminology'
        ) {
            dispatch(terms.actions.get(source, parameters.locale));
        }

        if (selectedEntity.pk !== this.props.machinery.entity) {
            dispatch(machinery.actions.get(source, locale, selectedEntity.pk));
        }

        if (selectedEntity.pk !== this.props.otherlocales.entity) {
            dispatch(
                otherlocales.actions.get(parameters.entity, parameters.locale),
            );
        }

        if (selectedEntity.pk !== this.props.teamComments.entity) {
            dispatch(teamcomments.actions.request(parameters.entity));
            dispatch(
                teamcomments.actions.get(parameters.entity, parameters.locale),
            );
        }
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
            source = utils.getOptimizedContent(
                selectedEntity.machinery_original,
                selectedEntity.format,
            );
            pk = selectedEntity.pk;
        }

        dispatch(machinery.actions.get(source, locale, pk));
    };

    copyLinkToClipboard = () => {
        const { locale, project, resource, entity } = this.props.parameters;
        const { protocol, host } = window.location;

        const string_link = `${protocol}//${host}/${locale}/${project}/${resource}/?string=${entity}`;
        navigator.clipboard.writeText(string_link).then(() => {
            // Notify the user of the change that happened.
            const notif = notification.messages.STRING_LINK_COPIED;
            this.props.dispatch(notification.actions.add(notif));
        });
    };

    goToNextEntity = () => {
        const { dispatch, nextEntity, router } = this.props;

        dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedChangesExist,
                this.props.unsavedChangesIgnored,
                () => {
                    dispatch(
                        navigation.actions.updateEntity(
                            router,
                            nextEntity.pk.toString(),
                        ),
                    );
                    dispatch(editor.actions.reset());
                },
            ),
        );
    };

    goToPreviousEntity = () => {
        const { dispatch, previousEntity, router } = this.props;

        dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedChangesExist,
                this.props.unsavedChangesIgnored,
                () => {
                    dispatch(
                        navigation.actions.updateEntity(
                            router,
                            previousEntity.pk.toString(),
                        ),
                    );
                    dispatch(editor.actions.reset());
                },
            ),
        );
    };

    navigateToPath = (path: string) => {
        const { dispatch } = this.props;

        dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedChangesExist,
                this.props.unsavedChangesIgnored,
                () => {
                    dispatch(push(path));
                },
            ),
        );
    };

    openLightbox = (image: string) => {
        this.props.dispatch(lightbox.actions.open(image));
    };

    updateEditorTranslation = (translation: string, changeSource: string) => {
        this.props.dispatch(editor.actions.update(translation, changeSource));
    };

    updateMachinerySources = (
        machinerySources: Array<SourceType>,
        machineryTranslation: string,
    ) => {
        this.props.dispatch(
            editor.actions.updateMachinerySources(
                machinerySources,
                machineryTranslation,
            ),
        );
    };

    addTextToEditorTranslation = (content: string, changeSource?: string) => {
        this.props.dispatch(
            editor.actions.updateSelection(content, changeSource),
        );
    };

    deleteTranslation = (translationId: number) => {
        const { parameters, pluralForm, dispatch } = this.props;
        dispatch(
            history.actions.deleteTranslation(
                parameters.entity,
                parameters.locale,
                pluralForm,
                translationId,
            ),
        );
    };

    setCommentTabIndex = (tab: number) => {
        this.setState({ commentTabIndex: tab });
    };

    setContactPerson = (contact: string) => {
        this.setState({ contactPerson: contact });
    };

    resetContactPerson = () => {
        this.setState({ contactPerson: '' });
    };

    addComment = (comment: string, translation: ?number) => {
        const { parameters, pluralForm, dispatch } = this.props;
        dispatch(
            comments.actions.addComment(
                parameters.entity,
                parameters.locale,
                pluralForm,
                translation,
                comment,
            ),
        );
    };

    togglePinnedStatus = (pinned: boolean, commentId: number) => {
        this.props.dispatch(
            teamcomments.actions.togglePinnedStatus(pinned, commentId),
        );
    };

    /*
     * This is a copy of EditorBase.updateTranslationStatus().
     * When changing this function, you probably want to change both.
     * We might want to refactor to keep the logic in one place only.
     */
    updateTranslationStatus = (
        translationId: number,
        change: ChangeOperation,
    ) => {
        const {
            locale,
            nextEntity,
            parameters,
            pluralForm,
            router,
            selectedEntity,
            dispatch,
        } = this.props;
        // No need to check for unsaved changes in `EditorBase.updateTranslationStatus()`,
        // because it cannot be triggered for the use case of bug 1508474.
        dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedChangesExist,
                this.props.unsavedChangesIgnored,
                () => {
                    dispatch(
                        history.actions.updateStatus(
                            change,
                            selectedEntity,
                            locale,
                            parameters.resource,
                            pluralForm,
                            translationId,
                            nextEntity,
                            router,
                        ),
                    );
                },
            ),
        );
    };

    render() {
        const state = this.props;

        if (!state.locale) {
            return null;
        }

        if (!state.selectedEntity) {
            return <section className='entity-details'></section>;
        }

        return (
            <section className='entity-details'>
                <section className='main-column'>
                    <EntityNavigation
                        copyLinkToClipboard={this.copyLinkToClipboard}
                        goToNextEntity={this.goToNextEntity}
                        goToPreviousEntity={this.goToPreviousEntity}
                    />
                    <Metadata
                        entity={state.selectedEntity}
                        isReadOnlyEditor={state.isReadOnlyEditor}
                        locale={state.locale}
                        pluralForm={state.pluralForm}
                        terms={state.terms}
                        openLightbox={this.openLightbox}
                        addTextToEditorTranslation={
                            this.addTextToEditorTranslation
                        }
                        navigateToPath={this.navigateToPath}
                        teamComments={state.teamComments}
                        user={state.user}
                        commentTabRef={this.commentTabRef}
                        setCommentTabIndex={this.setCommentTabIndex}
                        setContactPerson={this.setContactPerson}
                    />
                    <EditorSelector
                        fileFormat={state.selectedEntity.format}
                        key={state.selectedEntity.pk}
                    />
                    <history.History
                        entity={state.selectedEntity}
                        history={state.history}
                        isReadOnlyEditor={state.isReadOnlyEditor}
                        isTranslator={state.isTranslator}
                        locale={state.locale}
                        user={state.user}
                        deleteTranslation={this.deleteTranslation}
                        addComment={this.addComment}
                        users={state.users}
                        updateTranslationStatus={this.updateTranslationStatus}
                        updateEditorTranslation={this.updateEditorTranslation}
                    />
                </section>
                <section className='third-column'>
                    <Helpers
                        entity={state.selectedEntity}
                        isReadOnlyEditor={state.isReadOnlyEditor}
                        locale={state.locale}
                        machinery={state.machinery}
                        otherlocales={state.otherlocales}
                        teamComments={state.teamComments}
                        terms={state.terms}
                        addComment={this.addComment}
                        togglePinnedStatus={this.togglePinnedStatus}
                        users={state.users}
                        parameters={state.parameters}
                        user={state.user}
                        updateEditorTranslation={this.updateEditorTranslation}
                        updateMachinerySources={this.updateMachinerySources}
                        searchMachinery={this.searchMachinery}
                        addTextToEditorTranslation={
                            this.addTextToEditorTranslation
                        }
                        navigateToPath={this.navigateToPath}
                        commentTabRef={this.commentTabRef}
                        commentTabIndex={this.state.commentTabIndex}
                        setCommentTabIndex={this.setCommentTabIndex}
                        contactPerson={this.state.contactPerson}
                        resetContactPerson={this.resetContactPerson}
                    />
                </section>
            </section>
        );
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslationString: plural.selectors.getTranslationStringForSelectedEntity(
            state,
        ),
        history: state[history.NAME],
        isReadOnlyEditor: entities.selectors.isReadOnlyEditor(state),
        isTranslator: user.selectors.isTranslator(state),
        locale: state[locale.NAME],
        machinery: state[machinery.NAME],
        nextEntity: entities.selectors.getNextEntity(state),
        previousEntity: entities.selectors.getPreviousEntity(state),
        otherlocales: state[otherlocales.NAME],
        teamComments: state[teamcomments.NAME],
        terms: state[terms.NAME],
        parameters: navigation.selectors.getNavigationParams(state),
        pluralForm: plural.selectors.getPluralForm(state),
        router: state.router,
        selectedEntity: entities.selectors.getSelectedEntity(state),
        unsavedChangesExist: state[unsavedchanges.NAME].exist,
        unsavedChangesIgnored: state[unsavedchanges.NAME].ignored,
        user: state[user.NAME],
        users: state[user.NAME],
    };
};

export default connect(mapStateToProps)(EntityDetailsBase);
