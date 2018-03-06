
import React from 'react';

import {List, ListItem} from 'widgets/lists/generic';


export class MenuItem extends React.Component {

    get className () {
        return this.props.className || 'menu-item';
    }

    render () {
        return (
            <ListItem className={this.className}>
              {this.props.children}
            </ListItem>);
    }
}


export class Menu extends React.PureComponent {

    get className () {
        return this.props.className || 'menu';
    }

    get components () {
        const components = {item: MenuItem};
        return Object.assign({}, components, (this.props.components || {}));
    }

    get items () {
        return this.props.items.map(item => {
            return {value: item};
        });
    }

    render () {
        return (
            <List
               items={this.items}
               components={this.components}
               className={this.className} />);
    }
}
