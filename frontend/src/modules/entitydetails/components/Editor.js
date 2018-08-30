/* @flow */

import * as React from 'react';

import './Editor.css';

import type { DbEntity } from 'modules/entitieslist';


type Props = {|
    activeTranslation: string,
    selectedEntity: ?DbEntity,
    sendSuggestion: Function,
|};

type State = {|
    translation: string,
|};


/**
 * Editor for translation strings.
 */
export default class Editor extends React.Component<Props, State> {
    constructor(props: Props): void {
        super(props);
        this.state = {
            translation: props.activeTranslation,
        };
    }

    componentDidUpdate(prevProps: Props): void {
        if (this.props.activeTranslation !== prevProps.activeTranslation) {
            this.setState({
                translation: this.props.activeTranslation,
            });
        }
    }

    handleChange = (event: SyntheticInputEvent<HTMLTextAreaElement>): void => {
        this.setState({
            translation: event.currentTarget.value,
        });
    }

    copyOriginalIntoEditor = (): void => {
        const { selectedEntity } = this.props;
        if (selectedEntity) {
            this.setState({
                translation: selectedEntity.original,
            });
        }
    }

    clearEditor = (): void => {
        this.setState({
            translation: '',
        });
    }

    sendSuggestion = (): void => {
        this.props.sendSuggestion(this.state.translation);
    }

    render(): React.Node {
        return <div className="editor">
            <textarea
                value={ this.state.translation }
                onChange={ this.handleChange }
            />
            <div className="options">
                <button className="action-copy" onClick={ this.copyOriginalIntoEditor }>Copy</button>
                <button className="action-clear" onClick={ this.clearEditor }>Clear</button>
                <button className="action-send" onClick={ this.sendSuggestion }>Suggest</button>
            </div>
        </div>;
    }
}
