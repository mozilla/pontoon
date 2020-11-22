import React from 'react';

export default class Checkbox extends React.Component {
    /* A checkbox which you can set `indeterminate` on
     *
     */

    constructor(props) {
        super(props);
        this.el = {};
    }

    get indeterminate() {
        return this.props.indeterminate ? true : false;
    }

    componentDidMount() {
        this.el.indeterminate = this.indeterminate;
    }

    componentDidUpdate(prevProps) {
        if (prevProps.indeterminate !== this.props.indeterminate) {
            this.el.indeterminate = this.indeterminate;
        }
    }

    render() {
        const { indeterminate, ...props } = this.props;
        return (
            <input {...props} type='checkbox' ref={(el) => (this.el = el)} />
        );
    }
}
