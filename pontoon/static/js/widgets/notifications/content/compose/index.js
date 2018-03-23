
import React from 'react';

import {LocaleMultiSelector} from 'widgets/locale-selector';


class NotificationMessage extends React.PureComponent {

    handleCompose = (evt) => {
        this.props.handleCompose(evt.target.value);
    }

    render () {
        return (
            <div className="message-wrapper">
              <textarea onChange={this.handleCompose} />
              <p>Supports html</p>
            </div>);
    }
}

class Subtitle extends React.PureComponent {
    render () {
        return (
            <h3>
              <span className="stress">{this.props.prefix}</span> {this.props.subtitle}
            </h3>);
    }
}


export class NotificationCompose extends React.Component {
    state = {recipients: [], message: '', errors: {}};

    handleSelectLocales = (recipients) => {
        this.setState({recipients});
    }

    handleMessageCompose = (message) => {
        this.setState({message});
    }

    handleSubmit = (evt) => {
        evt.preventDefault();
        const {message, recipients} = this.state;
        const errors = {};
        if (!recipients.length) {
            errors.locales = 'Select at least one locale';
        }
        if (!message) {
            errors.message = 'Enter some message';
        }
        if (Object.keys(errors).length) {
            this.setState({errors});
        } else {
            const {message, recipients} = this.state;
            this.props.handleSubmit({message, selected_locales: recipients});
        }
    }

    render () {
        const {errors} = this.state;
        return (
            <div className="notifications-widget">
              <Subtitle prefix="#1" subtitle="Choose recipient teams" />
              <LocaleMultiSelector
                 errors={errors.locales}
                 handleSelect={this.handleSelectLocales}
                 locales={this.props.available_locales}
                 complete={this.props.complete}
                 incomplete={this.props.incomplete} />
              <Subtitle prefix="#2" subtitle="Enter notification message" />
              <NotificationMessage handleCompose={this.handleMessageCompose} />
              <menu className="controls">
                <button className="button active send" onClick={this.handleSubmit}>Send</button>
              </menu>
            </div>);
    }
}
