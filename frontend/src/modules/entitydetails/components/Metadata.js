/* @flow */

import * as React from 'react';
import { Link } from 'react-router-dom';
import Linkify from 'react-linkify';

import './Metadata.css';

import Screenshots from './Screenshots';
import type { DbEntity } from 'modules/entitieslist';


type PropertyProps = {|
    title: string,
    children: React.Node,
|};

/**
 * Component to dislay a property of an entity.
 *
 * Only used by Metadata.
 */
class Property extends React.Component<PropertyProps> {
    render(): React.Node {
        const { children, title } = this.props;
        const className = title.trim().toLowerCase().replace(/ /g, '-');
        return <p className={ className }>
            <span className="title">{ title }</span>
            <span className="content">{ children }</span>
        </p>;
    }
}


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
    renderComment(entity: DbEntity): React.Node {
        if (!entity.comment) {
            return null;
        }

        let comment = entity.comment;

        const parts = entity.comment.split('\n');
        if (parts[0].startsWith('MAX_LENGTH')) {
            // This comment contains a max length instruction. Remove that part.
            parts.shift();
            comment = parts.join('\n');
        }

        return <Property title='Comment'>
            <Linkify properties={ { target: '_blank', rel: 'noopener noreferrer' } }>
                { comment }
            </Linkify>
        </Property>;
    }

    renderSourceArray(source: Array<Array<string>>): React.Node {
        return <ul>{ source.map((value, key) => {
            return <li key={ key }><span>#:</span>{ value.join(':') }</li>;
        }) }</ul>;
    }

    renderSourceObject(source: Object): React.Node {
        const examples = Object.keys(source).map((value, key) => {
            if (source[value].example) {
                return `$${value.toUpperCase()}$: ${source[value].example}`;
            }
            return null;
        });

        if (!examples) {
            return null;
        }

        return <Property title='Placeholder Examples'>
            <Linkify properties={ { target: '_blank', rel: 'noopener noreferrer' } }>
                { examples.join(', ') }
            </Linkify>
        </Property>;
    }

    renderSources(entity: DbEntity): React.Node {
        if (!entity.source) {
            return null;
        }

        if (Array.isArray(entity.source)) {
            return this.renderSourceArray(entity.source);
        }

        return this.renderSourceObject(entity.source);
    }

    render(): React.Node {
        const { entity, locale } = this.props;

        return <div className="metadata">
            <Screenshots source={ entity.comment } locale={ locale } />
            <p className="original">{ entity.original }</p>
            { this.renderComment(entity) }
            { this.renderSources(entity) }
            <Property title='Resource'>
                <Link to={ `/${locale}/${entity.project.slug}/${entity.path}/` }>
                    { entity.path }
                </Link>
            </Property>
            <Property title='Project'>
                <a href={ `/${locale}/${entity.project.slug}/` }>
                    { entity.project.name }
                </a>
            </Property>
        </div>;
    }
}
