
import React from 'react';

import './info-list.css';

import {List, ListItem} from 'widgets/lists/generic';


export class InfoList extends React.PureComponent {

    get components () {
        const components = {item: InfoListItem};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        if (!this.props.items) {
            return '';
        }
        return (
            <List
               className={this.props.className || "details"}
               items={Object.entries(this.props.items)}
               components={this.components} />);
    }
}


export class InfoListItem extends React.PureComponent {

    get className () {
        return this.props.className || this.props[0].toLowerCase().replace(' ', '-');
    }

    render () {
        const k = this.props[0];
        const v = this.props[1];
        return (
            <ListItem className={this.className}>
              <span className="title">{k}</span>
              <span className="value overflow">{v}</span>
            </ListItem>);
    }
}
