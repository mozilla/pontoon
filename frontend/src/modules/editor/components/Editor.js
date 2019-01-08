/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react';

import './Editor.css';

import { PluralSelector } from 'core/plural';

import EditorProxy from './EditorProxy';

import type { DbEntity } from 'modules/entitieslist';


type Props = {|
    translation: string,
    entity: ?DbEntity,
    sendSuggestion: Function,
    pluralForm: number,
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
export default class Editor extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            translation: props.translation,
        };
    }

    componentDidUpdate(prevProps: Props) {
        if (this.props.translation !== prevProps.translation) {
            this.setState({
                translation: this.props.translation,
            });
        }
    }

    updateTranslation = (translation: string) => {
        this.setState({
            translation,
        });
    }

    copyOriginalIntoEditor = () => {
        const { entity, pluralForm } = this.props;
        if (entity) {
            if (pluralForm === -1 || pluralForm === 1) {
                this.setState({ translation: entity.original });
            }
            else {
                this.setState({ translation: entity.original_plural });
            }
        }
    }

    clearEditor = () => {
        this.setState({
            translation: '',
        });
    }

    sendSuggestion = () => {
        this.props.sendSuggestion(this.state.translation);
    }

    render() {
        return <div className="editor">
            <PluralSelector />
            <EditorProxy
                entity={ this.props.entity }
                translation={ this.state.translation }
                updateTranslation={ this.updateTranslation }
            />
            <div className="options">
                <div className="actions">
                    <Localized id="entitydetails-editor-button-copy">
                        <button
                            className="action-copy"
                            onClick={ this.copyOriginalIntoEditor }
                        >
                            Copy
                        </button>
                    </Localized>
                    <Localized id="entitydetails-editor-button-clear">
                        <button
                            className="action-clear"
                            onClick={ this.clearEditor }
                        >
                            Clear
                        </button>
                    </Localized>
                    <Localized id="entitydetails-editor-button-send">
                        <button
                            className="action-send"
                            onClick={ this.sendSuggestion }
                        >
                            Suggest
                        </button>
                    </Localized>
                </div>
                <div className="clearfix">
                </div>
            </div>
        </div>;
    }
}
