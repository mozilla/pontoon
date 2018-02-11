
import React from 'react';

import {CheckboxTable} from 'widgets/tables';


export default class TagResourceTable extends React.PureComponent {

    constructor (props) {
        super(props);
        this.renderResource = this.renderResource.bind(this);
    }

    get columnResource () {
        return {
            Header: "Resource",
            id: "type",
            Cell: this.renderResource};
    }

    get columns () {
        return [this.columnResource];
    }

    get submitClass () {
        return "tag-resources-associate";
    }

    get submitMessage () {
        const {type} = this.props;
        return type === 'assoc' ? 'Unlink resources': 'Link resources';
    }

    renderResource (item) {
        return <span>{item.original[0]}</span>;
    }

    render () {
        return (
            <CheckboxTable
               columns={this.columns}
               submitClass={this.submitClass}
               submitMessage={this.submitMessage}
               {...this.props}
               />);
    }
}
