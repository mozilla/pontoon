
import React from 'react';

import Humanize from 'humanize-plus';

import {ListItem} from 'widgets/lists/generic';


export default class ProgressChartLegendItem extends React.PureComponent {

    render () {
        const title = this.props[0];
        const value = this.props[1];
        const link = '?status=' + title;
        return (
            <ListItem className={title}>
              <a href={link}>
                <div className="title">{title}</div>
                <div className="value" data-value={value}>
                  {Humanize.intComma(value)}
                </div>
              </a>
            </ListItem>
        );
    }
}
