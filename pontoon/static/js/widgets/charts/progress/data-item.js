
import React from 'react';


export default class ProgressChartDataItem extends React.PureComponent {

    render () {
        return (
            <span
               className={this.props.className}
               style={{width: this.props.data + '%'}} />);
    }
}
