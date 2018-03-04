
import React from 'react';

import {Icon} from 'widgets/icons';


export default class NotificationsButton extends React.PureComponent {

    get iconName () {
        if (!this.props.toolbar || this.props.toolbar.notifications.length == 0) {
            return 'bell-o';
        }
        return 'bell';
    }

    render () {
        return <Icon name={this.iconName} />
    }
}
