
import React from 'react';

import {LocaleStatsTable} from 'widgets/tables';


export class TagLocalesStatsTable extends React.PureComponent {

    render () {
        if (!this.props.data || !this.props.data.tag) {
            return '';
        }
        return (
            <LocaleStatsTable
               data={this.props.data.tag.data}
               />);
    }
}
