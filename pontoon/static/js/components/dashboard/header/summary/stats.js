
import React from 'react';

import Humanize from 'humanize-plus';

import {List, ListItem} from 'widgets/lists/generic';


export class StatItem extends React.PureComponent {

    render () {
        const k = this.props[0];
        const v = this.props[1];
        return (
            <ListItem className={k.toLowerCase()}>
              <span className="fa status" />
              {v.label}
              <span
                 className="value"
                 data-value={v.value || 0}>
                {Humanize.intComma(v.value || 0)}
              </span>
            </ListItem>);
    }
}


export class SummaryStats extends React.PureComponent {

    render () {
        if (!this.props.stats) {
            return '';
        }
        return (
            <List
               className="legend"
               items={Object.entries(this.props.stats)}
               components={{item: StatItem}} />);
    }
}
