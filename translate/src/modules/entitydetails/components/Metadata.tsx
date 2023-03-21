import { Localized } from '@fluent/react';
import parse from 'html-react-parser';
import React, { useCallback, useContext, useLayoutEffect } from 'react';
// @ts-expect-error Working types are unavailable for react-linkify 0.2.2
import Linkify from 'react-linkify';

import type { Entity } from '~/api/entity';
import { Locale } from '~/context/Locale';
import type { TermState } from '~/modules/terms';
import type { UserState } from '~/modules/user';
import { OriginalString } from '~/modules/originalstring';
import type { TeamCommentState } from '~/modules/teamcomments';

import { ContextIssueButton } from './ContextIssueButton';
import { FluentAttribute } from './FluentAttribute';
import { Property } from './Property';
import { Screenshots } from './Screenshots';

import './Metadata.css';

type Props = {
  entity: Entity;
  terms: TermState;
  teamComments: TeamCommentState;
  user: UserState;
  commentTabRef: React.RefObject<{ _reactInternalFiber: { index: number } }>;
  navigateToPath: (path: string) => void;
  setCommentTabIndex: (id: number) => void;
  setContactPerson: (contact: string) => void;
};

const Datum = ({
  children,
  className,
  id,
  title,
}: {
  children: React.ReactNode;
  className?: string;
  id: string;
  title: string;
}) =>
  children ? (
    <Localized id={'entitydetails-Metadata--' + id} attrs={{ title: true }}>
      <Property title={title} className={className ?? 'comment'}>
        <Linkify properties={{ target: '_blank', rel: 'noopener noreferrer' }}>
          {children}
        </Linkify>
      </Property>
    </Localized>
  ) : null;

function PinnedComments({ teamComments }: { teamComments: TeamCommentState }) {
  /* We can safely use parse with pinned comment content as it is
   * sanitized when coming from the DB. See:
   *   - pontoon.base.forms.AddCommentForm(}
   *   - pontoon.base.forms.HtmlField()
   */
  return (
    <>
      {teamComments?.comments
        .filter((comment) => comment.pinned)
        .map(({ content, id }) => (
          <Datum id='pinned-comment' key={id} title='PINNED COMMENT'>
            {parse(content)}
          </Datum>
        ))}
    </>
  );
}

function EntityComment({ comment }: { comment: string }) {
  // Remove any max length instructions
  return (
    <Datum id='comment' title='COMMENT'>
      {comment?.replace(/^MAX_LENGTH.*\n?/, '')}
    </Datum>
  );
}

function GroupComment({ comment }: { comment: string }) {
  return (
    <Datum id='group-comment' title='GROUP COMMENT'>
      {comment}
    </Datum>
  );
}

function ResourceComment({ comment }: { comment: string }) {
  const ref = React.useRef<HTMLDivElement>(null);
  const [overflow, setOverflow] = React.useState(false);
  const [expand, setExpand] = React.useState(false);

  useLayoutEffect(() => {
    const body = ref.current?.querySelector<HTMLDivElement>('.comment');
    if (body && body.scrollWidth > body.offsetWidth) {
      setOverflow(true);
    }
  }, []);

  return !comment ? null : (
    <div className='resource-comment' ref={ref}>
      <Datum
        className={expand ? 'comment expanded' : 'comment'}
        id='resource-comment'
        title='RESOURCE COMMENT'
      >
        {comment}
      </Datum>
      {overflow && !expand && (
        <Localized id='entitydetails-Metadata--see-more'>
          <button onClick={() => setExpand(true)}>See More</button>
        </Localized>
      )}
    </div>
  );
}

function EntityContext({ context }: { context: string }) {
  return (
    <Datum className='context' id='context' title='CONTEXT'>
      {context}
    </Datum>
  );
}

function SourceArray({ source }: { source: string[][] }) {
  return source.length > 1 || (source.length === 1 && source[0]) ? (
    <ul>
      {source.map((value, i) => (
        <li key={i}>
          <span className='title'>#:</span>
          {value.join(':')}
        </li>
      ))}
    </ul>
  ) : null;
}

function SourceObject({
  source,
}: {
  source: Record<string, { example?: string }>;
}) {
  const examples: string[] = [];
  for (const [value, { example }] of Object.entries(source)) {
    // Only placeholders with examples
    if (example) {
      examples.push(`$${value.toUpperCase()}$: ${example}`);
    }
  }

  return (
    <Datum
      className='placeholder'
      id='placeholder'
      title='PLACEHOLDER EXAMPLES'
    >
      {examples.join(', ')}
    </Datum>
  );
}

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
export function Metadata({
  commentTabRef,
  entity,
  navigateToPath,
  setCommentTabIndex,
  setContactPerson,
  terms,
  teamComments,
  user,
}: Props): React.ReactElement {
  const { code } = useContext(Locale);

  const navigateToPath_ = useCallback(
    (ev: React.MouseEvent<HTMLAnchorElement>) => {
      ev.preventDefault();
      navigateToPath(ev.currentTarget.pathname);
    },
    [navigateToPath],
  );

  const openTeamComments = useCallback(() => {
    const teamCommentsTab = commentTabRef.current;
    const index = teamCommentsTab?._reactInternalFiber.index ?? 0;
    setCommentTabIndex(index);
    setContactPerson(entity.project.contact.name);
  }, [entity, setCommentTabIndex, setContactPerson]);

  const contactPerson = entity.project.contact;
  const showContextIssueButton = user.isAuthenticated && contactPerson;

  return (
    <div className='metadata'>
      {showContextIssueButton && (
        <ContextIssueButton openTeamComments={openTeamComments} />
      )}
      <Screenshots source={entity.comment} locale={code} />
      <OriginalString navigateToPath={navigateToPath} terms={terms} />
      <PinnedComments teamComments={teamComments} />
      <EntityComment comment={entity.comment} />
      <GroupComment comment={entity.group_comment} />
      <ResourceComment comment={entity.resource_comment} key={entity.pk} />
      <FluentAttribute entity={entity} />
      <EntityContext context={entity.context} />
      {Array.isArray(entity.source) ? (
        <SourceArray source={entity.source} />
      ) : entity.source ? (
        <SourceObject source={entity.source} />
      ) : null}
      <Localized id='entitydetails-Metadata--resource' attrs={{ title: true }}>
        <Property title='RESOURCE' className='resource'>
          <a href={`/${code}/${entity.project.slug}/`}>{entity.project.name}</a>
          <span className='divider'>&bull;</span>
          <a
            href={`/${code}/${entity.project.slug}/${entity.path}/`}
            onClick={navigateToPath_}
            className='resource-path'
          >
            {entity.path}
          </a>
        </Property>
      </Localized>
    </div>
  );
}
