
import React from 'react';

import LatestActivityTooltipFooter from './footer'
import LatestActivityTooltipTranslation from './translation'


export default class LatestActivityTooltip extends React.PureComponent {

    render () {
        return (
            <span>
              <LatestActivityTooltipTranslation
                 translation={this.props.translation.string} />
              <LatestActivityTooltipFooter
                 action={this.props.action}
                 date={this.props.date}
                 user={this.props.user} />
            </span>);
    }
}
