/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react';

import './Editor.css';

import * as locales from 'core/locales';
import * as navigation from 'core/navigation';
import * as plural from 'core/plural';
import * as user from 'core/user';
import * as entitieslist from 'modules/entitieslist';
import * as entitydetails from 'modules/entitydetails';
import * as history from 'modules/history';
import * as unsavedchanges from 'modules/unsavedchanges';

import { actions, NAME } from '..';
import FailedChecks from './FailedChecks';
import EditorProxy from './EditorProxy';
import EditorSettings from './EditorSettings';
import KeyboardShortcuts from './KeyboardShortcuts';
import TranslationLength from './TranslationLength';

import type { EditorState } from '../reducer';
import type { Locale } from 'core/locales';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import { withActionsDisabled } from 'core/utils';
import type { DbEntity } from 'modules/entitieslist';
import type { ChangeOperation } from 'modules/history';


type Props = {|
    activeTranslation: string,
    editor: EditorState,
    isReadOnlyEditor: boolean,
    locale: Locale,
    nextEntity: DbEntity,
    parameters: NavigationParams,
    pluralForm: number,
    router: Object,
    selectedEntity: ?DbEntity,
    user: UserState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
    isActionDisabled: boolean,
    disableAction: () => void,
|};


/**
 * Editor for translation strings.
 *
 * Will present a different editor depending on the file format of the string,
 * see `EditorProxy` for more information.
 */
export class EditorBase extends React.Component<InternalProps> {
    resetSelectionContent = () => {
        this.props.dispatch(actions.resetSelection());
    }

    updateTranslation = (translation: string, fromOutsideEditor?: boolean) => {
        const { activeTranslation } = this.props;
        const source = fromOutsideEditor ? 'external' : 'internal';

        this.props.dispatch(
            actions.update(translation, source)
        );

        this.props.dispatch(
            unsavedchanges.actions.update(translation, activeTranslation)
        );
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
        this.updateTranslation('');
    }

    sendTranslation = (ignoreWarnings: ?boolean) => {
        if (this.props.isActionDisabled) {
            return;
        }
        this.props.disableAction();

        const state = this.props;

        if (!state.selectedEntity || !state.locale) {
            return;
        }

        this.props.dispatch(actions.sendTranslation(
            state.selectedEntity.pk,
            state.editor.translation,
            state.locale,
            state.selectedEntity.original,
            state.pluralForm,
            state.user.settings.forceSuggestions,
            state.nextEntity,
            state.router,
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
            ignoreWarnings,
        ));
    }

    resetFailedChecks = () => {
        this.props.dispatch(actions.resetFailedChecks());
    }

    render() {
        if (!this.props.locale) {
            return null;
        }

        return <div className="editor">
            <plural.PluralSelector />
            <EditorProxy
                isReadOnlyEditor={ this.props.isReadOnlyEditor }
                entity={ this.props.selectedEntity }
                editor={ this.props.editor }
                locale={ this.props.locale }
                copyOriginalIntoEditor={ this.copyOriginalIntoEditor }
                resetFailedChecks={ this.resetFailedChecks }
                resetSelectionContent={ this.resetSelectionContent }
                sendTranslation={ this.sendTranslation }
                updateTranslation={ this.updateTranslation }
                updateTranslationStatus={ this.updateTranslationStatus }
            />
            <menu>
                <FailedChecks
                    source={ this.props.editor.source }
                    user={ this.props.user }
                    errors={ this.props.editor.errors }
                    warnings={ this.props.editor.warnings }
                    resetFailedChecks={ this.resetFailedChecks }
                    sendTranslation={ this.sendTranslation }
                    updateTranslationStatus={ this.updateTranslationStatus }
                />
                <unsavedchanges.UnsavedChanges />
                { !this.props.user.isAuthenticated ?
                    <Localized
                        id="editor-editor-sign-in-to-translate"
                        a={
                            <user.SignInLink url={ this.props.user.signInURL }></user.SignInLink>
                        }
                    >
                        <p className='banner'>
                            { '<a>Sign in</a> to translate.' }
                        </p>
                    </Localized>
                : (this.props.selectedEntity && this.props.selectedEntity.readonly) ?
                    <Localized
                        id="editor-editor-read-only-localization"
                    >
                        <p className='banner'>This is a read-only localization.</p>
                    </Localized>
                :
                    <React.Fragment>
                        <EditorSettings
                            settings={ this.props.user.settings }
                            updateSetting={ this.updateSetting }
                        />
                        <KeyboardShortcuts />
                        <TranslationLength
                            entity={ this.props.selectedEntity }
                            pluralForm={ this.props.pluralForm }
                            translation={ this.props.editor.translation }
                        />
                        <div className="actions">
                            <Localized id="editor-editor-button-copy">
                                <button
                                    className="action-copy"
                                    onClick={ this.copyOriginalIntoEditor }
                                >
                                    Copy
                                </button>
                            </Localized>
                            <Localized id="editor-editor-button-clear">
                                <button
                                    className="action-clear"
                                    onClick={ this.clearEditor }
                                >
                                    Clear
                                </button>
                            </Localized>
                            { this.props.user.settings.forceSuggestions ?
                            // Suggest button, will send an unreviewed translation.
                            <Localized id="editor-editor-button-suggest">
                                <button
                                    className="action-suggest"
                                    disabled={ this.props.isActionDisabled }
                                    onClick={ this.sendTranslation }
                                >
                                    Suggest
                                </button>
                            </Localized>
                            :
                            // Save button, will send an approved translation.
                            <Localized id="editor-editor-button-save">
                                <button
                                    className="action-save"
                                    disabled={ this.props.isActionDisabled }
                                    onClick={ this.sendTranslation }
                                >
                                    Save
                                </button>
                            </Localized>
                            }
                        </div>
                        <div className="clearfix" />
                    </React.Fragment>
                }
            </menu>
        </div>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslation: entitydetails.selectors.getTranslationForSelectedEntity(state),
        editor: state[NAME],
        isReadOnlyEditor: entitydetails.selectors.isReadOnlyEditor(state),
        locale: locales.selectors.getCurrentLocaleData(state),
        nextEntity: entitieslist.selectors.getNextEntity(state),
        parameters: navigation.selectors.getNavigationParams(state),
        pluralForm: plural.selectors.getPluralForm(state),
        router: state.router,
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        user: state[user.NAME],
    };
};

export default withActionsDisabled(connect(mapStateToProps)(EditorBase));
