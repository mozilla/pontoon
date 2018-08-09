/* @flow */

import * as React from 'react';
import { Link } from 'react-router-dom';

import './Metadata.css';

import type { DbEntity } from 'modules/entitieslist';


type Props = {|
    entity: DbEntity,
    locale: string,
|};


/**
 * Component showing metadata of an entity.
 *
 * Shows:
 *  - the original string
 *  - a comment (if any)
 *  - a list of source files (if any)
 *  - a link to the resource
 *  - a link to the project
 */
export default class Metadata extends React.Component<Props> {
    renderComment(): React.Node {
        const { entity } = this.props;

        if (!entity.comment) {
            return null;
        }

        return <p><span>Comment</span>{ entity.comment }</p>;
    }

    renderSources(): React.Node {
        const { entity } = this.props;

        if (!entity.source) {
            return null;
        }

        return <ul>{ entity.source.map((value, key) => {
            return <li key={ key }><span>#:</span>{ value.join(':') }</li>;
        }) }</ul>;
    }

    render(): React.Node {
        const { entity, locale } = this.props;

        return <div className="metadata">
            <p className="original">{ entity.original }</p>
            { this.renderComment() }
            { this.renderSources() }
            <p>
                <span>Resource</span>
                <Link to={ `/${locale}/${entity.project.slug}/${entity.path}/` }>
                    { entity.path }
                </Link>
            </p>
            <p>
                <span>Project</span>
                <a href={ `/${locale}/${entity.project.slug}/` }>
                    { entity.project.name }
                </a>
            </p>
        </div>;
    }
}
