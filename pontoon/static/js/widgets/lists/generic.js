
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

    get components () {
        const components = {item: ListItem};
        return Object.assign({}, components, (this.props.components || {}));
    }

    render () {
        const {className, items, ...props} = this.props;
        if (!items) {
            return '';
        }
        const {item, ...components} = this.components;
        const Item = item;
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
