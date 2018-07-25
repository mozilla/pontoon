/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';

import './Editor.css';

import { suggest } from '../actions';

import * as entitieslist from 'modules/entitieslist';
import { selectors as navSelectors } from 'core/navigation';

import type { DbEntity } from 'modules/entitieslist';
import type { Navigation } from 'core/navigation';


type Props = {|
    activeTranslation: string,
    navigation: Navigation,
    selectedEntity: ?DbEntity,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

type State = {|
    translation: string,
|};


export class EditorBase extends React.Component<InternalProps, State> {
    constructor(props: InternalProps): void {
        super(props);
        this.state = {
            translation: props.activeTranslation,
        };
    }

    componentDidUpdate(prevProps: InternalProps): void {
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
        const { navigation, selectedEntity } = this.props;
        const { entity, locale } = navigation;

        if (!selectedEntity) {
            return;
        }

        this.props.dispatch(suggest(
            entity,
            this.state.translation,
            locale,
            selectedEntity.original,
        ));
    }

    render(): React.Node {
        return (<div className="editor">
            <textarea
                value={ this.state.translation }
                onChange={ this.handleChange }
            />
            <div className="options">
                <button className="action-copy" onClick={ this.copyOriginalIntoEditor }>Copy</button>
                <button className="action-clear" onClick={ this.clearEditor }>Clear</button>
                <button className="action-send" onClick={ this.sendSuggestion }>Suggest</button>
            </div>
        </div>);
    }
};


const mapStateToProps = (state: Object): Props => {
    return {
        activeTranslation: entitieslist.selectors.getTranslationForSelectedEntity(state),
        selectedEntity: entitieslist.selectors.getSelectedEntity(state),
        navigation: navSelectors.getNavigation(state),
    };
};

export default connect(mapStateToProps)(EditorBase);
