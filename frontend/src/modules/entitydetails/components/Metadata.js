/* @flow */

import * as React from 'react';
import Linkify from 'react-linkify';
import { Localized } from '@fluent/react';

import './Metadata.css';

import FluentAttribute from './FluentAttribute';
import OriginalStringProxy from './OriginalStringProxy';
import Property from './Property';
import Screenshots from './Screenshots';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locale';


type Props = {|
    +entity: Entity,
    +isReadOnlyEditor: boolean,
    +locale: Locale,
    +pluralForm: number,
    +openLightbox: (string) => void,
    +addTextToEditorTranslation: (string) => void,
    +navigateToPath: (string) => void,
|};

type State = {|
    seeMore: boolean,
    isNotTruncated: boolean
|};


/**
 * Component showing metadata of an entity.
 *
 * Shows:
 *  - the original string
 *  - a comment (if any)
 *  - a group comment (if any)
 *  - a resource comment (if any)
 *  - a context (if any)
 *  - a list of source files (if any)
 *  - a link to the resource
 *  - a link to the project
 */
export default class Metadata extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            seeMore: false,
            isNotTruncated: false
        };
        this.span = React.createRef();
    }

    componentDidMount() {
        this.setState({
            isNotTruncated: this.isEllispsisActivated()
            });
        }

    componentDidUpdate(prevProps: Props) {
        if (this.props.entity !== prevProps.entity) {
            this.setState({ seeMore: false });
        }
    }

    isEllispsisActivated = () => {
        const span = this.span.current;
        const element = span.querySelector('span.target')

        return  element.getBoundingClientRect().width < element.scrollWidth
    };

    handleClickOnSeeMore = () => {
        this.setState({ seeMore: true });
    };
    
    handleClickOnPlaceable = (e: SyntheticMouseEvent<HTMLParagraphElement>) => {
        if (this.props.isReadOnlyEditor) {
            return;
        }
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
                this.props.addTextToEditorTranslation(e.target.childNodes[0].data);
            }
        }
    }

    renderComment(entity: Entity): React.Node {
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

        return <Localized id='entitydetails-Metadata--comment' attrs={ { title: true } }>
            <Property title='Comment' className='comment'>
                <Linkify properties={ { target: '_blank', rel: 'noopener noreferrer' } }>
                    { comment }
                </Linkify>
            </Property>
        </Localized>;
    }

    renderGroupComment(entity: Entity): React.Node {
        if (!entity.group_comment) {
            return null;
        }

        return <Localized id='entitydetails-Metadata--group-comment' attrs={ { title: true } }>
            <Property title='Group Comment' className='comment'>
                <Linkify properties={ { target: '_blank', rel: 'noopener noreferrer' } }>
                    { entity.group_comment }
                </Linkify>
            </Property>
        </Localized>;
    }

    renderResourceComment(entity: Entity): React.Node {
        const { seeMore, isNotTruncated } = this.state;

        if (!entity.resource_comment) {
            return null;
        }

        return <Localized id='entitydetails-Metadata--resource-comment' attrs={ { title: true } }>
            <Property
                title='Resource Comment'
                className={ seeMore ? 'comment' : 'comment truncate' }
            >
                <Linkify
                    properties={ { target: '_blank', rel: 'noopener noreferrer' } }
                    className='target'
                >
                    { entity.resource_comment }
                </Linkify>
                { isNotTruncated || seeMore ? null :
                    <Localized id='entitydetails-Metadata--see-more'>
                        <button onClick={ this.handleClickOnSeeMore }>
                            { 'See More' }
                        </button>
                    </Localized>
                }
            </Property>
        </Localized>;
    }

    renderContext(entity: Entity): React.Node {
        if (!entity.key) {
            return null;
        }

        return <Localized id='entitydetails-Metadata--context' attrs={ { title: true } }>
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

        return <Localized id='entitydetails-Metadata--placeholder' attrs={ { title: true } }>
            <Property title='Placeholder Examples' className='placeholder'>
                <Linkify properties={ { target: '_blank', rel: 'noopener noreferrer' } }>
                    { examples.join(', ') }
                </Linkify>
            </Property>
        </Localized>;
    }

    renderSources(entity: Entity): React.Node {
        if (!entity.source) {
            return null;
        }

        if (Array.isArray(entity.source)) {
            return this.renderSourceArray(entity.source);
        }

        return this.renderSourceObject(entity.source);
    }

    navigateToPath = (event: SyntheticMouseEvent<HTMLAnchorElement>) => {
        event.preventDefault();

        const path = event.currentTarget.pathname;
        this.props.navigateToPath(path);
    }

    render(): React.Node {
        const { entity, locale, openLightbox, pluralForm } = this.props;

        return <div className="metadata" ref={ this.span }>
            <Screenshots
                source={ entity.comment }
                locale={ locale.code }
                openLightbox={ openLightbox }
            />
            <OriginalStringProxy
                entity={ entity }
                locale={ locale }
                pluralForm={ pluralForm }
                handleClickOnPlaceable={ this.handleClickOnPlaceable }
            />
            { this.renderComment(entity) }
            { this.renderGroupComment(entity) }
            { this.renderResourceComment(entity) }
            <FluentAttribute entity={ entity } />
            { this.renderContext(entity) }
            { this.renderSources(entity) }
            <Localized id='entitydetails-Metadata--resource' attrs={ { title: true } }>
                <Property title='Resource' className='resource'>
                    <a
                        href={ `/${locale.code}/${entity.project.slug}/${entity.path}/` }
                        onClick={ this.navigateToPath }
                    >
                        { entity.path }
                    </a>
                </Property>
            </Localized>
            <Localized id='entitydetails-Metadata--project' attrs={ { title: true } }>
                <Property title='Project' className='project'>
                    <a href={ `/${locale.code}/${entity.project.slug}/` }>
                        { entity.project.name }
                    </a>
                </Property>
            </Localized>
        </div>;
    }
}
