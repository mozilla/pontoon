
import React from 'react';

import {getComponents} from 'utils/components';
import {List, ListItem} from 'widgets/lists/generic';


export class MenuItem extends React.Component {
    className = 'menu-item';

    render () {
        if (!this.props.children) {
            return <ListItem className="menu-item horizontal-separator" />;
        }
        return (
            <ListItem className={this.props.className || this.className}>
              {this.props.children}
            </ListItem>);
    }
}


export class Menu extends React.PureComponent {
    className = 'menu';
    components = {item: MenuItem};

    get items () {
        return this.props.items.map(item => {
            return {value: item};
        });
    }

    render () {
        return (
            <List
               items={this.items}
               components={getComponents(this)}
               className={this.props.className || this.className} />);
    }
}
