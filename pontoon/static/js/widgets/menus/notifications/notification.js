
import React from 'react';


export default class Notification extends React.PureComponent {

    render () {
        return (
            <div className="item-content">
              {this.renderActor()}
              {this.renderVerb()}
              {this.renderTarget()}
              {this.renderTime()}
              {this.renderDescription()}
            </div>);
    }

    renderActor () {
        const {actor} = this.props;
        if (!actor) {
            return '';
        }
        return (
            <span className="actor">
              <a href={actor.url}>
                {actor.anchor}
              </a>
            </span>);
    }

    renderDescription () {
        const {description} = this.props;
        return <div className="message">{description}</div>;
    }

    renderTarget () {
        const {url, target} = this.props;
        if (!target) {
            return '';
        }
        return (
            <span className="target">
              <a href={url}>{target}</a>
            </span>);
    }

    renderTime () {
        const {ago} = this.props;
        if (!ago) {
            return '';
        }
        return <p className="timeago">{ago} ago</p>;
    }

    renderVerb () {
        const {verb} = this.props;
        return <span className="verb">{verb}</span>;
    }
}
