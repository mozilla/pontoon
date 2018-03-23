
import React from 'react';

import {SanitizedHTML} from 'widgets/sanitized';

import './notification.css';


export class Notification extends React.PureComponent {

    render () {
        const {actor, ago, message, target, verb} = this.props;
        return (
            <div className="notification-item">
              {actor ? this.renderActor(actor) : ''}
              {this.renderVerb(verb)}
              {target ? this.renderTarget(target) : ''}
              {ago ? this.renderTime(ago) : ''}
              {this.renderDescription(message)}
            </div>);
    }

    renderActor (actor) {
        return (
            <span className="actor">
              <a href={actor.url}>
                {actor.anchor}
              </a>
            </span>);
    }

    renderDescription (description) {
        return <SanitizedHTML className="message" html={description} />
    }

    renderTarget (target) {
        const {name, url} = target;
        return (
            <span className="target">
              <a href={url}>{name}</a>
            </span>);
    }

    renderTime (ago) {
        return <p className="timeago">{ago} ago</p>;
    }

    renderVerb (verb) {
        return <span className="verb">{verb}</span>;
    }
}
