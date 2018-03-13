
import React from 'react';


export function componentManager(WrappedComponent, Components) {

    return class Wrapper extends React.PureComponent {

        render() {
            let {components} = this.props;
            return (
                <WrappedComponent
                   {...this.props}
                   components={Object.assign({}, (components || {}), (Components || {}))}
                   />);
            }
    }
}
