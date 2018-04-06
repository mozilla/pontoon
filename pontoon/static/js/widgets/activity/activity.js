
import React from 'react';

import "./activity.css";

import {LatestActivityTooltip} from './tooltip';


export default class LatestActivity extends React.Component {
    components = {tooltip: LatestActivityTooltip};
    state = {showTooltip: false};

    popTooltip = () => {
        this.setState({showTooltip: true});
    }

    unpopTooltip = () => {
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
        if (!showTooltip) {
            return '';
        }
        const {components, ...props} = this.props;
        const {tooltip: Tooltip = this.components.tooltip} = (components || {});
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
