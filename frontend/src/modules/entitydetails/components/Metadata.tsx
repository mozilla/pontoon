import * as React from 'react';
import Linkify from 'react-linkify';
import { Localized } from '@fluent/react';
import parse from 'html-react-parser';

import './Metadata.css';

import ContextIssueButton from './ContextIssueButton';
import FluentAttribute from './FluentAttribute';
import OriginalStringProxy from './OriginalStringProxy';
import Property from './Property';
import Screenshots from './Screenshots';
import TermsPopup from './TermsPopup';

import type { Entity, TermType } from 'core/api';
import type { Locale } from 'core/locale';
import type { TermState } from 'core/term';
import type { TeamCommentState } from 'modules/teamcomments';
import type { UserState } from 'core/user';

type Props = {
    readonly entity: Entity;
    readonly isReadOnlyEditor: boolean;
    readonly locale: Locale;
    readonly pluralForm: number;
    readonly terms: TermState;
    readonly teamComments: TeamCommentState;
    readonly user: UserState;
    readonly commentTabRef: Record<string, any>;
    readonly openLightbox: (arg0: string) => void;
    readonly addTextToEditorTranslation: (text: string) => void;
    readonly navigateToPath: (path: string) => void;
    setCommentTabIndex: (id: number) => void;
    setContactPerson: (contact: string) => void;
};

type State = {
    popupTerms: Array<TermType>;
    seeMore: boolean;
};

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
            popupTerms: [],
            seeMore: false,
        };
    }

    componentDidUpdate(prevProps: Props) {
        if (this.props.entity !== prevProps.entity) {
            this.setState({
                popupTerms: [],
                seeMore: false,
            });
        }
    }

    handleClickOnSeeMore: () => void = () => {
        this.setState({ seeMore: true });
    };

    handleClickOnPlaceable: (
        e: React.MouseEvent<HTMLParagraphElement>,
    ) => void = (e: React.MouseEvent<HTMLParagraphElement>) => {
        const target = e.target;
        if (!(target instanceof HTMLElement)) {
            return;
        }
        if (target && target.classList.contains('placeable')) {
            if (this.props.isReadOnlyEditor) {
                return;
            }
            if (target.dataset['match']) {
                this.props.addTextToEditorTranslation(target.dataset['match']);
            } else if (target.firstChild) {
                const child = target.firstChild;
                if (child instanceof Text) {
                    this.props.addTextToEditorTranslation(child.data);
                }
            }
        }

        // Handle click on Term
        const markedTerm = target.dataset['term'];
        if (target && markedTerm) {
            const popupTerms = this.props.terms.terms.filter(
                (t) => t.text === markedTerm,
            );
            this.setState({ popupTerms: popupTerms });
        }
    };

    hidePopupTerms: () => void = () => {
        this.setState({ popupTerms: [] });
    };

    renderComment(entity: Entity): React.ReactNode {
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

        return (
            <Localized
                id='entitydetails-Metadata--comment'
                attrs={{ title: true }}
            >
                <Property title='COMMENT' className='comment'>
                    <Linkify
                        properties={{
                            target: '_blank',
                            rel: 'noopener noreferrer',
                        }}
                    >
                        {comment}
                    </Linkify>
                </Property>
            </Localized>
        );
    }

    renderGroupComment(entity: Entity): React.ReactNode {
        if (!entity.group_comment) {
            return null;
        }

        return (
            <Localized
                id='entitydetails-Metadata--group-comment'
                attrs={{ title: true }}
            >
                <Property title='GROUP COMMENT ' className='comment'>
                    <Linkify
                        properties={{
                            target: '_blank',
                            rel: 'noopener noreferrer',
                        }}
                    >
                        {entity.group_comment}
                    </Linkify>
                </Property>
            </Localized>
        );
    }

    renderPinnedComments(teamComments: TeamCommentState): React.ReactNode {
        if (!teamComments) {
            return null;
        }

        const pinnedComments = teamComments.comments.filter((comment) => {
            return comment.pinned === true;
        });

        return (
            <>
                {!pinnedComments
                    ? null
                    : pinnedComments.map((pinnedComment) => {
                          return (
                              <Localized
                                  id='entitydetails-Metadata--pinned-comment'
                                  attrs={{ title: true }}
                                  key={pinnedComment.id}
                              >
                                  <Property
                                      title='PINNED COMMENT'
                                      className='comment'
                                  >
                                      <Linkify
                                          properties={{
                                              target: '_blank',
                                              rel: 'noopener noreferrer',
                                          }}
                                      >
                                          {/* We can safely use parse with pinnedComment.content as it is
                                           * sanitized when coming from the DB. See:
                                           *   - pontoon.base.forms.AddCommentForm(}
                                           *   - pontoon.base.forms.HtmlField()
                                           */}
                                          {parse(pinnedComment.content)}
                                      </Linkify>
                                  </Property>
                              </Localized>
                          );
                      })}
            </>
        );
    }

    renderResourceComment(entity: Entity): React.ReactNode {
        const { seeMore } = this.state;
        const MAX_LENGTH = 85;

        if (!entity.resource_comment) {
            return null;
        }

        let comment = entity.resource_comment;

        return (
            <Localized
                id='entitydetails-Metadata--resource-comment'
                attrs={{ title: true }}
            >
                <Property title='RESOURCE COMMENT' className='comment'>
                    <Linkify
                        properties={{
                            target: '_blank',
                            rel: 'noopener noreferrer',
                        }}
                    >
                        {comment.length < MAX_LENGTH || seeMore
                            ? comment
                            : comment.slice(0, MAX_LENGTH) + '\u2026'}
                    </Linkify>
                    {comment.length < MAX_LENGTH || seeMore ? null : (
                        <Localized id='entitydetails-Metadata--see-more'>
                            <button onClick={this.handleClickOnSeeMore}>
                                {'See More'}
                            </button>
                        </Localized>
                    )}
                </Property>
            </Localized>
        );
    }

    renderContext(entity: Entity): React.ReactNode {
        if (!entity.context) {
            return null;
        }

        return (
            <Localized
                id='entitydetails-Metadata--context'
                attrs={{ title: true }}
            >
                <Property title='CONTEXT' className='context'>
                    {entity.context}
                </Property>
            </Localized>
        );
    }

    renderSourceArray(source: Array<Array<string>>): React.ReactNode {
        if (!source.length || (source.length === 1 && !source[0])) {
            return null;
        }

        return (
            <ul>
                {source.map((value, key) => {
                    return (
                        <li key={key}>
                            <span className='title'>#:</span>
                            {value.join(':')}
                        </li>
                    );
                })}
            </ul>
        );
    }

    renderSourceObject(source: Record<string, any>): React.ReactNode {
        const examples: string[] = [];
        for (const [value, { example }] of Object.entries(source)) {
            // Only placeholders with examples
            if (example) {
                examples.push(`$${value.toUpperCase()}$: ${example}`);
            }
        }

        if (examples.length === 0) {
            return null;
        }

        return (
            <Localized
                id='entitydetails-Metadata--placeholder'
                attrs={{ title: true }}
            >
                <Property title='PLACEHOLDER EXAMPLES' className='placeholder'>
                    <Linkify
                        properties={{
                            target: '_blank',
                            rel: 'noopener noreferrer',
                        }}
                    >
                        {examples.join(', ')}
                    </Linkify>
                </Property>
            </Localized>
        );
    }

    renderSources(entity: Entity): React.ReactNode {
        if (!entity.source) {
            return null;
        }

        if (Array.isArray(entity.source)) {
            return this.renderSourceArray(entity.source);
        }

        return this.renderSourceObject(entity.source);
    }

    navigateToPath: (event: React.MouseEvent<HTMLAnchorElement>) => void = (
        event: React.MouseEvent<HTMLAnchorElement>,
    ) => {
        event.preventDefault();

        const path = event.currentTarget.pathname;
        this.props.navigateToPath(path);
    };

    openTeamComments: () => void = () => {
        const teamCommentsTab = this.props.commentTabRef.current;
        const index = teamCommentsTab._reactInternalFiber.index;
        this.props.setCommentTabIndex(index);
        this.props.setContactPerson(this.props.entity.project.contact.name);
    };

    render(): React.ReactNode {
        const {
            entity,
            isReadOnlyEditor,
            locale,
            openLightbox,
            pluralForm,
            terms,
            user,
            teamComments,
        } = this.props;
        const { popupTerms } = this.state;
        const contactPerson = entity.project.contact;
        const showContextIssueButton = user.isAuthenticated && contactPerson;

        return (
            <div className='metadata'>
                {!showContextIssueButton ? null : (
                    <ContextIssueButton
                        openTeamComments={this.openTeamComments}
                    />
                )}
                <Screenshots
                    source={entity.comment}
                    locale={locale.code}
                    openLightbox={openLightbox}
                />
                <OriginalStringProxy
                    entity={entity}
                    locale={locale}
                    pluralForm={pluralForm}
                    terms={terms}
                    handleClickOnPlaceable={this.handleClickOnPlaceable}
                />
                {popupTerms.length > 0 && (
                    <TermsPopup
                        isReadOnlyEditor={isReadOnlyEditor}
                        locale={locale.code}
                        terms={popupTerms}
                        addTextToEditorTranslation={
                            this.props.addTextToEditorTranslation
                        }
                        hide={this.hidePopupTerms}
                        navigateToPath={this.props.navigateToPath}
                    />
                )}
                {this.renderPinnedComments(teamComments)}
                {this.renderComment(entity)}
                {this.renderGroupComment(entity)}
                {this.renderResourceComment(entity)}
                <FluentAttribute entity={entity} />
                {this.renderContext(entity)}
                {this.renderSources(entity)}
                <Localized
                    id='entitydetails-Metadata--resource'
                    attrs={{ title: true }}
                >
                    <Property title='RESOURCE' className='resource'>
                        <a href={`/${locale.code}/${entity.project.slug}/`}>
                            {entity.project.name}
                        </a>
                        <span className='divider'>&bull;</span>
                        <a
                            href={`/${locale.code}/${entity.project.slug}/${entity.path}/`}
                            onClick={this.navigateToPath}
                            className='resource-path'
                        >
                            {entity.path}
                        </a>
                    </Property>
                </Localized>
            </div>
        );
    }
}
