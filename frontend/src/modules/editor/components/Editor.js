/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react';

import './Editor.css';

import * as locales from 'core/locales';
import * as plural from 'core/plural';
import * as user from 'core/user';
import * as entitieslist from 'modules/entitieslist';
import * as entitydetails from 'modules/entitydetails';

import { actions, NAME } from '..';
import EditorProxy from './EditorProxy';
import EditorSettings from './EditorSettings';
import KeyboardShortcuts from './KeyboardShortcuts';

import type { Locale } from 'core/locales';
import type { UserState } from 'core/user';
import type { DbEntity } from 'modules/entitieslist';
import type { EditorState } from '../reducer';


type Props = {|
    editor: EditorState,
    isReadOnlyEditor: boolean,
    locale: ?Locale,
    nextEntity: DbEntity,
    pluralForm: number,
    router: Object,
    selectedEntity: ?DbEntity,
    user: UserState,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
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
        const source = fromOutsideEditor ? 'external' : 'internal';
        this.props.dispatch(actions.update(translation, source));
    }

    copyOriginalIntoEditor = () => {
        const { selectedEntity, pluralForm } = this.props;
        if (selectedEntity) {
            if (pluralForm === -1 || pluralForm === 1) {
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

    sendTranslation = () => {
        const state = this.props;

        if (!state.selectedEntity || !state.locale) {
            return;
        }

        this.props.dispatch(actions.sendTranslation(
            state.selectedEntity.pk,
            state.editor.translation,
            state.locale.code,
            state.selectedEntity.original,
            state.pluralForm,
            state.user.settings.forceSuggestions,
            state.nextEntity,
            state.router,
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
                resetSelectionContent={ this.resetSelectionContent }
                sendTranslation={ this.sendTranslation }
                updateTranslation={ this.updateTranslation }
            />
            <menu>
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
        editor: state[NAME],
        isReadOnlyEditor: entitydetails.selectors.isReadOnlyEditor(state),
        locale: locales.selectors.getCurrentLocaleData(state),
        nextEntity: entitieslist.selectors.getNextEntity(state),
        pluralForm: plural.selectors.getPluralForm(state),
        router: state.router,
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        user: state[user.NAME],
    };
};

export default connect(mapStateToProps)(EditorBase);
