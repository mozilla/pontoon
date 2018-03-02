
import React from 'react';


export const getComponent = (component, name) => {
    const {components, props} = component;
    const {[name]: Component=(components || {})[name]} = (props.components || {});
    return Component;
}


export const getComponents = (parent) => {
    return {...parent.components, ...(parent.props.components || {})}
}


export function componentManager(WrappedComponent, Components) {

    return class Wrapper extends React.PureComponent {

        render() {
            let {components, ...props} = this.props;
            return (
                <WrappedComponent
                   {...props}
                   components={Object.assign({}, (Components || {}), (components || {}))}
                   />);
            }
    }
}
