
import React from 'react';

import {Columns} from 'widgets/columns';
import {SearchControls} from 'widgets/search';
import {List} from 'widgets/lists/generic';

import './locale-selector.css';


export class LocaleItem extends React.PureComponent {
    render () {
        return <a name={this.props.pk} onClick={this.props.handleClick}>{this.props.name} <span>{this.props.code}</span></a>;
    }
}


export class LocaleMultiSelector extends React.Component {
    state = {chosen: new Set()};

    get columns () {
        return [
            [this.renderSelectable(), 1],
            [this.renderChosen(), 1]];
    }

    handleClick = (evt) => {
        evt.preventDefault();
        const {name} = evt.currentTarget;
        this.setState(prevState => {
            if (name === 'remove') {
                return {chosen: new Set()};
            } else if (name === 'all') {
                return {chosen: new Set(Object.values(this.props.locales || {}).map(v => v.pk))};
            } else if (['complete', 'incomplete'].includes(name)) {
                return {chosen: new Set(this.props[name])};
            }
            return {chosen: new Set([...prevState.chosen].concat([parseInt(name)]))};
        });
    }

    componentDidUpdate (prevProps, prevState) {
        if (prevState !== this.state) {
            if (this.props.handleSelect) {
                this.props.handleSelect([...this.state.chosen]);
            }
        }
    }

    get selectable () {
        return this._locales();
    }

    get chosen () {
        return this._locales(true);
    }

    _locales (_chosen) {
        const {chosen} = this.state;
        const options = Object.values(this.props.locales || {}).map(v => {
            if (chosen.has(v.pk) === (_chosen ? true : false)) {
                return {value: <LocaleItem {...v} />};
            }});
        return options.filter(v => v);
    }

    renderSelectable () {
        return (
            <div className="menu permanent available">
              <label htmlFor="available">
                Available
                <a name="all" className="all" onClick={this.handleClick}>Choose all →</a>
              </label>
              <SearchControls />
              <List items={this.selectable} />
            </div>);
    }

    renderChosen () {
        return (
            <div className="menu permanent chosen">
              <label htmlFor="chosen">
                Chosen
                <a name="remove" className="remove" onClick={this.handleClick}>← Remove all</a>
              </label>
              <SearchControls />
              <List items={this.chosen} />
            </div>);
    }

    render () {
        return [<Columns className="locale-selector" columns={this.columns} />,
                this.renderToolbar()];
    }

    renderErrors () {
        return (
            <div className="errors">
              <p>{this.props.errors}</p>
            </div>);
    }

    renderToolbar () {
        return (
            <div className="toolbar clearfix">
              <div className="shortcuts clearfix">
                <a className="complete" name="complete" onClick={this.handleClick}>Complete only &rarr;</a>
                <a className="incomplete" name="incomplete" onClick={this.handleClick}>Incomplete only &rarr;</a>
              </div>
              {this.props.errors ? this.renderErrors() : ''}
            </div>);
    }
}
