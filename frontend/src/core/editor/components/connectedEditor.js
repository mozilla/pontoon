/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './connectedEditor.css';

import * as entities from 'core/entities';
import * as locale from 'core/locale';
import * as navigation from 'core/navigation';
import * as notification from 'core/notification';
import * as plural from 'core/plural';
import * as user from 'core/user';
import * as history from 'modules/history';
import * as search from 'modules/search';
import * as unsavedchanges from 'modules/unsavedchanges';

import { NAME, actions } from '..';

import { withActionsDisabled } from 'core/utils';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locale';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { ChangeOperation } from 'modules/history';
import type { SearchAndFilters } from 'modules/search';
import type { UnsavedChangesState } from 'modules/unsavedchanges';
import type { EditorState } from '../reducer';
import type { Translation } from '../actions';


type Props = {|
    activeTranslation: string,
    editor: EditorState,
    isReadOnlyEditor: boolean,
    locale: Locale,
    nextEntity: Entity,
    parameters: NavigationParams,
    pluralForm: number,
    router: Object,
    searchAndFilters: SearchAndFilters,
    selectedEntity: Entity,
    unsavedchanges: UnsavedChangesState,
    user: UserState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
    isActionDisabled: boolean,
    disableAction: () => void,
|};

export type EditorProps = {|
    activeTranslation: string,
    editor: EditorState,
    entity: Entity,
    isReadOnlyEditor: boolean,
    locale: Locale,
    pluralForm: number,
    searchInputFocused: boolean,
    unsavedchanges: UnsavedChangesState,
    user: UserState,
    updateFocusedOrFirstField: (content: string) => void,
    clearEditor: () => void,
    copyOriginalIntoEditor: () => void,
    handleShortcuts: (
        event: SyntheticKeyboardEvent<HTMLTextAreaElement>,
        sendTranslation: ?(ignoreWarnings?: boolean, translation?: string) => void,
        clearEditor: ?() => void,
        copyOriginalIntoEditor: ?() => void,
    ) => void,
    resetFailedChecks: () => void,
    resetFocusedOrFirstFieldContent: () => void,
    resetSelectionContent: () => void,
    sendTranslation: (ignoreWarnings?: boolean, translation?: string) => void,
    setInitialTranslation: (Translation) => void,
    showNotSupportedMessage: () => void,
    updateTranslation: (Translation, fromOutsideEditor?: boolean) => void,
    updateTranslationStatus: (number, ChangeOperation, ?boolean) => void,
    hideUnsavedChanges: () => void,
    ignoreUnsavedChanges: () => void,
    updateUnsavedChanges: (translation?: Translation, initial?: Translation) => void,
    updateSetting: (string, boolean) => void,
|};


/**
 * Higher-Order Component to create a connected Editor.
 *
 * Provides all methods needed to run an Editor, as well as data
 * from the store. Renders nothing if the application is not ready
 * yet (locale hasn't been loaded).
 */
export default function connectedEditor<Object>(
    WrappedComponent: React.AbstractComponent<EditorProps>
): React.AbstractComponent<Object> {
    class EditorBase extends React.Component<InternalProps> {
        resetSelectionContent = () => {
            this.props.dispatch(actions.resetSelection());
        }

        updateTranslation = (translation: Translation, fromOutsideEditor?: boolean) => {
            const source = fromOutsideEditor ? 'external' : 'internal';
            this.props.dispatch(actions.update(translation, source));
        }

        updateFocusedOrFirstField = (content: string) => {
            this.props.dispatch(actions.updateFocusedOrFirstField(content));
        }

        resetFocusedOrFirstFieldContent = () => {
            this.props.dispatch(actions.resetFocusedOrFirstField());
        }

        hideUnsavedChanges = () => {
            this.props.dispatch(unsavedchanges.actions.hide());
        }

        ignoreUnsavedChanges = () => {
            this.props.dispatch(unsavedchanges.actions.ignore());
        }

        updateUnsavedChanges = (translation?: Translation, initial?: Translation) => {
            const props = this.props;

            if (!translation) {
                translation = props.editor.translation;
            }

            if (!initial) {
                initial = props.editor.initialTranslation || props.activeTranslation;
            }

            this.props.dispatch(unsavedchanges.actions.update(translation, initial));
        }

        handleShortcuts = (
            event: SyntheticKeyboardEvent<HTMLTextAreaElement>,
            sendTranslation: ?(ignoreWarnings?: boolean, translation?: string) => void,
            clearEditor: ?() => void,
            copyOriginalIntoEditor: ?() => void,
        ) => {
            sendTranslation = sendTranslation || this.sendTranslation;
            clearEditor = clearEditor || this.clearEditor;
            copyOriginalIntoEditor = copyOriginalIntoEditor || this.copyOriginalIntoEditor;

            const key = event.keyCode;

            let handledEvent = false;

            // On Enter:
            //   - If unsaved changes popup is shown, leave anyway.
            //   - If failed checks popup is shown after approving a translation, approve it anyway.
            //   - In other cases, send current translation.
            if (key === 13 && !event.ctrlKey && !event.shiftKey && !event.altKey) {
                if (this.props.isActionDisabled) {
                    event.preventDefault();
                    return;
                }
                this.props.disableAction();

                handledEvent = true;

                const errors = this.props.editor.errors;
                const warnings = this.props.editor.warnings;
                const source = this.props.editor.source;
                const ignoreWarnings = !!(errors.length || warnings.length);

                // Leave anyway
                if (this.props.unsavedchanges.shown) {
                    this.ignoreUnsavedChanges();
                }
                // Approve anyway
                else if (typeof(source) === 'number') {
                    this.updateTranslationStatus(source, 'approve', ignoreWarnings);
                }
                // Send translation
                else {
                    sendTranslation(ignoreWarnings);
                }
            }

            // On Esc, close unsaved changes and failed checks popups if open.
            if (key === 27) {
                handledEvent = true;

                const errors = this.props.editor.errors;
                const warnings = this.props.editor.warnings;

                // Close unsaved changes popup
                if (this.props.unsavedchanges.shown) {
                    this.hideUnsavedChanges();
                }
                // Close failed checks popup
                else if (errors.length || warnings.length) {
                    this.resetFailedChecks();
                }
            }

            // On Ctrl + Shift + C, copy the original translation.
            if (key === 67 && event.ctrlKey && event.shiftKey && !event.altKey) {
                handledEvent = true;
                copyOriginalIntoEditor();
            }

            // On Ctrl + Shift + Backspace, clear the content.
            if (key === 8 && event.ctrlKey && event.shiftKey && !event.altKey) {
                handledEvent = true;
                clearEditor();
            }

            if (handledEvent) {
                event.preventDefault();
            }
        }

        copyOriginalIntoEditor = () => {
            const { selectedEntity, pluralForm } = this.props;
            if (selectedEntity) {
                if (pluralForm === -1 || pluralForm === 0) {
                    this.updateTranslation(selectedEntity.original, true);
                }
                else {
                    this.updateTranslation(selectedEntity.original_plural, true);
                }
            }
        }

        clearEditor = () => {
            this.updateTranslation('', true);
        }

        sendTranslation = (ignoreWarnings?: boolean, translation?: string) => {
            const props = this.props;

            if (!props.selectedEntity || !props.locale) {
                return;
            }

            const content = translation || props.editor.translation;
            if (typeof(content) !== 'string') {
                throw new Error(
                    'Trying to save an unsupported non-string translation: ' +
                    typeof(content)
                );
            }

            this.props.dispatch(actions.sendTranslation(
                props.selectedEntity,
                content,
                props.locale,
                props.pluralForm,
                props.user.settings.forceSuggestions,
                props.nextEntity,
                props.router,
                props.parameters.resource,
                ignoreWarnings,
            ));
        }

        updateSetting = (setting: string, value: boolean) => {
            this.props.dispatch(
                user.actions.saveSetting(
                    setting,
                    value,
                    this.props.user.username,
                )
            );
        }

        /*
         * This is a copy of EntityDetailsBase.updateTranslationStatus().
         * When changing this function, you probably want to change both.
         * We might want to refactor to keep the logic in one place only.
         */
        updateTranslationStatus = (translationId: number, change: ChangeOperation, ignoreWarnings: ?boolean) => {
            const { locale, nextEntity, parameters, pluralForm, router, selectedEntity, dispatch } = this.props;
            dispatch(history.actions.updateStatus(
                change,
                selectedEntity,
                locale,
                parameters.resource,
                pluralForm,
                translationId,
                nextEntity,
                router,
                ignoreWarnings,
            ));
        }

        setInitialTranslation = (translation: Translation) => {
            this.props.dispatch(actions.setInitialTranslation(translation));
        }

        resetFailedChecks = () => {
            this.props.dispatch(actions.resetFailedChecks());
        }

        showNotSupportedMessage = () => {
            this.props.dispatch(
                notification.actions.add(
                    notification.messages.FTL_NOT_SUPPORTED_RICH_EDITOR
                )
            );
        }

        render() {
            if (!this.props.locale) {
                return null;
            }

            return <div className="editor">
                <WrappedComponent
                    activeTranslation={ this.props.activeTranslation }
                    isReadOnlyEditor={ this.props.isReadOnlyEditor }
                    entity={ this.props.selectedEntity }
                    editor={ this.props.editor }
                    locale={ this.props.locale }
                    pluralForm={ this.props.pluralForm }
                    searchInputFocused={ this.props.searchAndFilters.searchInputFocused }
                    unsavedchanges={ this.props.unsavedchanges }
                    user={ this.props.user }
                    updateFocusedOrFirstField={ this.updateFocusedOrFirstField }
                    clearEditor={ this.clearEditor }
                    copyOriginalIntoEditor={ this.copyOriginalIntoEditor }
                    handleShortcuts={ this.handleShortcuts }
                    resetFailedChecks={ this.resetFailedChecks }
                    resetFocusedOrFirstFieldContent={ this.resetFocusedOrFirstFieldContent }
                    resetSelectionContent={ this.resetSelectionContent }
                    sendTranslation={ this.sendTranslation }
                    setInitialTranslation={ this.setInitialTranslation }
                    showNotSupportedMessage={ this.showNotSupportedMessage }
                    updateTranslation={ this.updateTranslation }
                    updateTranslationStatus={ this.updateTranslationStatus }
                    hideUnsavedChanges={ this.hideUnsavedChanges }
                    ignoreUnsavedChanges={ this.ignoreUnsavedChanges }
                    updateUnsavedChanges={ this.updateUnsavedChanges }
                    updateSetting={ this.updateSetting }
                />
            </div>;
        }
    }

    const mapStateToProps = (state: Object): Props => {
        return {
            activeTranslation: plural.selectors.getTranslationForSelectedEntity(state),
            editor: state[NAME],
            isReadOnlyEditor: entities.selectors.isReadOnlyEditor(state),
            locale: state[locale.NAME],
            nextEntity: entities.selectors.getNextEntity(state),
            parameters: navigation.selectors.getNavigationParams(state),
            pluralForm: plural.selectors.getPluralForm(state),
            router: state.router,
            searchAndFilters: state[search.NAME],
            selectedEntity: entities.selectors.getSelectedEntity(state),
            unsavedchanges: state[unsavedchanges.NAME],
            user: state[user.NAME],
        };
    };

    return withActionsDisabled(connect(mapStateToProps)(EditorBase));
}
