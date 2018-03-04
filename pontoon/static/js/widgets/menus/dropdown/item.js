
import React from 'react';

import {ListItem} from 'widgets/lists/generic';


export default class DropdownMenuItem extends React.PureComponent {

    render () {
        if (!this.props.children) {
            return <ListItem className="menu-item horizontal-separator" />;
        }
        return <ListItem className="menu-item">{this.props.children}</ListItem>;
    }
}
