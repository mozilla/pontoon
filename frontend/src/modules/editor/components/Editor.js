/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import debounce from 'lodash.debounce';
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
    activeTranslation: string,
    editor: EditorState,
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

type State = {|
    translation: string,
|};


/**
 * Editor for translation strings.
 *
 * Will present a different editor depending on the file format of the string,
 * see `EditorProxy` for more information.
 */
export class EditorBase extends React.Component<InternalProps, State> {
    constructor(props: InternalProps) {
        super(props);

        // This state acts as a buffer between the Editors and the editor state.
        // We want to avoid updating the redux state at every key stroke, thus
        // we keep track of changes in this state and only update the store
        // every few milliseconds using debouce.
        this.state = {
            translation: props.activeTranslation,
        };
    }

    componentDidUpdate(prevProps: InternalProps) {
        if (prevProps.editor.translation !== this.props.editor.translation) {
            this.updateTranslation(this.props.editor.translation);
        }
    }

    resetSelectionContent = () => {
        this.props.dispatch(actions.updateSelection(''));
    }

    updateTranslation = (translation: string) => {
        this.setState({ translation });

        if (translation !== this.props.editor.translation) {
            this.updateStoreTranslation(translation);
        }
    }

    // We want to keep the store in sync with the local state, so that potential
    // changes made outside the editor are based on a translation that is as
    // current as possible. We still keep a short delay to avoid having
    // performance issues.
    updateStoreTranslation = debounce((translation: string) => {
        this.props.dispatch(actions.update(translation));
    }, 200)

    updateSetting = (setting: string, value: boolean) => {
        this.props.dispatch(
            user.actions.saveSetting(
                setting,
                value,
                this.props.user.username,
            )
        );
    }

    copyOriginalIntoEditor = () => {
        const { selectedEntity, pluralForm } = this.props;
        if (selectedEntity) {
            if (pluralForm === -1 || pluralForm === 1) {
                this.updateTranslation(selectedEntity.original);
            }
            else {
                this.updateTranslation(selectedEntity.original_plural);
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
            this.state.translation,
            state.locale.code,
            state.selectedEntity.original,
            state.pluralForm,
            state.user.settings.forceSuggestions,
            state.nextEntity,
            state.router,
        ));
    }

    // Return true if editor must be read-only, which happens when:
    //   - the user is not authenticated or
    //   - the entity is read-only
    isReadOnlyEditor = () => {
        if (!this.props.user.isAuthenticated || this.props.selectedEntity.readonly) {
            return true;
        }
        return false;
    }

    render() {
        if (!this.props.locale) {
            return null;
        }

        return <div className="editor">
            <plural.PluralSelector />
            <EditorProxy
                readOnly={ this.isReadOnlyEditor() }
                entity={ this.props.selectedEntity }
                editor={ this.props.editor }
                translation={ this.state.translation }
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
            : this.props.selectedEntity.readonly ?
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
        activeTranslation: entitydetails.selectors.getTranslationForSelectedEntity(state),
        editor: state[NAME],
        locale: locales.selectors.getCurrentLocaleData(state),
        nextEntity: entitieslist.selectors.getNextEntity(state),
        pluralForm: plural.selectors.getPluralForm(state),
        router: state.router,
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        user: state[user.NAME],
    };
};

export default connect(mapStateToProps)(EditorBase);
