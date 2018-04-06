
import React from 'react';

import {Columns} from 'widgets/columns';

import {NotificationsMenu} from './menu'
import {NotificationsContent} from './content'

import './notifications.css';


export default class Notifications extends React.PureComponent {
    state = {content: 'compose'};

    handleMenuChange = (name) => {
        this.setState({content: name});
    }

    get columns () {
        const {content} = this.state;
        return [
            [<NotificationsMenu {...this.props.data} handleMenuChange={this.handleMenuChange} />, 17],
            [<NotificationsContent {...this.props.data} content={content} handleSubmit={this.props.handleSubmit} />, 32]];
    }

    render () {
        return <Columns className="manual-notifications" columns={this.columns} />;
    }
}
