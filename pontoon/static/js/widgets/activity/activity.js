
import React from 'react';

import "./activity.css";

import {LatestActivityTooltip} from './tooltip';


export default class LatestActivity extends React.Component {

    constructor (props) {
        super(props);
        this.popTooltip = this.popTooltip.bind(this);
        this.unpopTooltip = this.unpopTooltip.bind(this);
        this.state = {showTooltip: false};
    }

    get components () {
        const components = {tooltip: LatestActivityTooltip};
        return Object.assign({}, components, (this.props.components || {}));
    }

    popTooltip () {
        this.setState({showTooltip: true});
    }

    unpopTooltip () {
        this.setState({showTooltip: false});
    }

    renderTime () {
        return (
            <time>
              {this.props.ago}
            </time>);
    }

    renderTooltip () {
        const {showTooltip} = this.state;
        const {tooltip: Tooltip} = this.components;
        if (!showTooltip) {
            return '';
        }
        const {components, ...props} = this.props;
        return (
            <aside className="tooltip">
              <Tooltip {...props} />
            </aside>);
    }

    render () {
        return (
            <div className="wrapper">
              <div className="latest-activity-inline">
                <span
                   className="latest-inline"
                   onMouseLeave={this.unpopTooltip}
                   onMouseEnter={this.popTooltip}>
                  {this.renderTime()}
                  {this.renderTooltip()}
                </span>
              </div>
            </div>);
    }
}
