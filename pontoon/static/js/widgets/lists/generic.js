
import React from 'react';


export class ListItem extends React.PureComponent {

    render () {
        return (
            <li className={this.props.className}>
              {this.props.children}
            </li>);
    }
}


export class List extends React.PureComponent {
    components = {item: ListItem};

    render () {
        const {className, items, ...props} = this.props;
        if (!items) {
            return '';
        }
        const {item: Item = this.components.item, ...components} = (this.props.components || {});
        return (
            <ul className={className}>
              {items.map((v, key) => {
                  const {label, value, ...itemProps} = v;
                  return (
                      <Item
                         {...props}
                         {...itemProps}
                         components={components}
                         key={key}>
                        {value || label}
                      </Item>);
              })}
            </ul>);
    }
}
