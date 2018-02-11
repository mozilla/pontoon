
import React from 'react';

import Datetime from 'utils/datetime';


export default class LatestActivityTooltipFooter extends React.PureComponent {

    constructor (props) {
        super(props);
        this.datetime = new Datetime(this.props.date);
    }

    renderByline () {
        if (this.props.user && this.props.user.name) {
            return (
                <span>
                  by <span className="translation-author">{this.props.user.name}</span>
                </span>);
        }
        return '';
    }

    renderAvatar () {
        if (this.props.user && this.props.user.avatar) {
            return (
                <img
                   className="rounded"
                   height="44"
                   width="44"
                   src={this.props.user.avatar} />);
        }
        return '';
    }

    renderAction () {
        return (
            <p className="translation-action">
              <span>{this.props.action}</span>
              {this.renderByline()}
            </p>);
    }

    renderDatetime () {
        return (
            <p className="translation-time">
              on {this.datetime.date}
              at {this.datetime.time}
            </p>);
    }

    render () {
        return (
            <footer className="clearfix">
              <div className="wrapper">
                <div className="translation-details">
                  {this.renderAction()}
                  {this.renderDatetime()}
                </div>
                {this.renderAvatar()}
              </div>
            </footer>);
    }
}
