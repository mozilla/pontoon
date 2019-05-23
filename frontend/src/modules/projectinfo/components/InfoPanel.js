/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import './InfoPanel.css';


type Props = {|
    info: string,
|};

type State = {|
    visible: boolean,
|};


/**
 * Show a panel with the information provided for the current project.
 */
export class InfoPanelBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the search panel.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    render() {
        return <div className="info-panel">
            <div className="button" onClick={ this.toggleVisibility }>
                <span className="fa fa-info"></span>
            </div>
            { !this.state.visible ? null : <div className="panel">
                <h2>Project Info</h2>
                <p dangerouslySetInnerHTML={ { __html: this.props.info } } />
            </div> }
        </div>;
    }
}


export default onClickOutside(InfoPanelBase);
