/* @flow */

import * as React from 'react';
import { Link } from 'react-router-dom';
import Linkify from 'react-linkify';
import { Localized } from 'fluent-react';

import './Metadata.css';

import { WithPlaceables } from 'core/placeable';

import Screenshots from './Screenshots';

import type { Locale } from 'core/locales';
import type { DbEntity } from 'modules/entitieslist';


type PropertyProps = {|
    +title: string,
    +className: string,
    +children: React.Node,
|};


/**
 * Component to dislay a property of an entity.
 *
 * Only used by Metadata.
 */
class Property extends React.Component<PropertyProps> {
    render(): React.Node {
        const { children, className, title } = this.props;
        return <p className={ className }>
            <span className="title">{ title }</span>
            <span className="content">{ children }</span>
        </p>;
    }
}


type Props = {|
    +entity: DbEntity,
    +locale: Locale,
    +pluralForm: number,
    +openLightbox: (string) => void,
    +addTextToEditorTranslation: (string) => void,
|};


/**
 * Component showing metadata of an entity.
 *
 * Shows:
 *  - the original string
 *  - a comment (if any)
 *  - a context (if any)
 *  - a list of source files (if any)
 *  - a link to the resource
 *  - a link to the project
 */
export default class Metadata extends React.Component<Props> {
    handleClickOnPlaceable = (e: SyntheticMouseEvent<HTMLParagraphElement>) => {
        // Flow requires that we use `e.currentTarget` instead of `e.target`.
        // However in this case, we do want to use that, so I'm ignoring all
        // errors Flow throws there.
        // $FLOW_IGNORE
        if (e.target && e.target.classList.contains('placeable')) {
            // $FLOW_IGNORE
            if (e.target.dataset['match']) {
                this.props.addTextToEditorTranslation(
                    // $FLOW_IGNORE
                    e.target.dataset['match']
                );
            }
            // $FLOW_IGNORE
            else if (e.target.childNodes.length) {
                // $FLOW_IGNORE
                this.props.addTextToEditorTranslation(e.target.childNodes[0].data);
            }
        }
    }

    getOriginalContent(entity: DbEntity) {
        const { pluralForm, locale } = this.props;

        if (pluralForm === -1) {
            return {
                title: null,
                original: entity.original,
            };
        }

        if (locale.cldrPlurals[pluralForm] === 1) {
            return {
                title: <Localized id='entitydetails-metadata-singular'>
                    <h2>Singular</h2>
                </Localized>,
                original: entity.original,
            };
        }

        return {
            title: <Localized id='entitydetails-metadata-plural'>
                <h2>Plural</h2>
            </Localized>,
            original: entity.original_plural,
        };
    }

    renderOriginal(entity: DbEntity): React.Node {
        const { title, original } = this.getOriginalContent(entity);

        return <React.Fragment>
            { title }
            <p className="original" onClick={ this.handleClickOnPlaceable }>
                <WithPlaceables>
                    { original }
                </WithPlaceables>
            </p>
        </React.Fragment>;
    }

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

        return <Localized id='entitydetails-metadata-comment' attrs={ { title: true } }>
            <Property title='Comment' className='comment'>
                <Linkify properties={ { target: '_blank', rel: 'noopener noreferrer' } }>
                    { comment }
                </Linkify>
            </Property>
        </Localized>;
    }

    renderContext(entity: DbEntity): React.Node {
        if (!entity.key) {
            return null;
        }

        return <Localized id='entitydetails-metadata-context' attrs={ { title: true } }>
            <Property title='Context' className='context'>
                { entity.key }
            </Property>
        </Localized>;
    }

    renderSourceArray(source: Array<Array<string>>): React.Node {
        if (!source.length || (source.length === 1 && !source[0])) {
            return null;
        }

        return <ul>{ source.map((value, key) => {
            return <li key={ key }><span className="title">#:</span>{ value.join(':') }</li>;
        }) }</ul>;
    }

    renderSourceObject(source: Object): React.Node {
        const examples = Object.keys(source).map(value => {
            if (!source[value].example) {
                return null;
            }
            return `$${value.toUpperCase()}$: ${source[value].example}`;
        });

        if (!examples) {
            return null;
        }

        return <Localized id='entitydetails-metadata-placeholder' attrs={ { title: true } }>
            <Property title='Placeholder Examples' className='placeholder'>
                <Linkify properties={ { target: '_blank', rel: 'noopener noreferrer' } }>
                    { examples.join(', ') }
                </Linkify>
            </Property>
        </Localized>;
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
        const { entity, locale, openLightbox } = this.props;

        return <div className="metadata">
            <Screenshots
                source={ entity.comment }
                locale={ locale.code }
                openLightbox={ openLightbox }
            />
            { this.renderOriginal(entity) }
            { this.renderComment(entity) }
            { this.renderContext(entity) }
            { this.renderSources(entity) }
            <Localized id='entitydetails-metadata-resource' attrs={ { title: true } }>
                <Property title='Resource' className='resource'>
                    <Link to={ `/${locale.code}/${entity.project.slug}/${entity.path}/` }>
                        { entity.path }
                    </Link>
                </Property>
            </Localized>
            <Localized id='entitydetails-metadata-project' attrs={ { title: true } }>
                <Property title='Project' className='project'>
                    <a href={ `/${locale.code}/${entity.project.slug}/` }>
                        { entity.project.name }
                    </a>
                </Property>
            </Localized>
        </div>;
    }
}
