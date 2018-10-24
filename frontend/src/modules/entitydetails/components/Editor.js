/* @flow */

import * as React from 'react';
import { Localized } from 'fluent-react/compat';

import './Editor.css';

import { PluralSelector } from 'core/plural';

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

    handleChange = (event: SyntheticInputEvent<HTMLTextAreaElement>) => {
        this.setState({
            translation: event.currentTarget.value,
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
            <textarea
                value={ this.state.translation }
                onChange={ this.handleChange }
            />
            <div className="options">
                <Localized id="editor-button-copy">
                    <button className="action-copy" onClick={ this.copyOriginalIntoEditor }>Copy</button>
                </Localized>
                <Localized id="editor-button-clear">
                    <button className="action-clear" onClick={ this.clearEditor }>Clear</button>
                </Localized>
                <Localized id="editor-button-send">
                    <button className="action-send" onClick={ this.sendSuggestion }>Suggest</button>
                </Localized>
            </div>
        </div>;
    }
}
