
import React from 'react';

import Datetime from 'utils/datetime';


export class Deadline extends React.PureComponent {

    render () {
        if (!this.props.deadline) {
            return <span>No deadline set</span>;
        }
        const deadline = new Date(this.props.deadline);
        const now = new Date();
        let className = '';
        if (now > deadline) {
            className = 'overdue';
        }
        return (
            <time className={className} dateTime={this.props.deadline}>
              {new Datetime(this.props.deadline).date}
            </time>
        );
    }
}
