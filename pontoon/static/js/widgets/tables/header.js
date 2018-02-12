
import React from 'react';


export default class TableHeader extends React.PureComponent {

    render () {
        const {id, className} = this.props;
        return (
            <div id={id} className={className}>
              {this.props.children}
              <i className="fa" />
            </div>);
    }
}
