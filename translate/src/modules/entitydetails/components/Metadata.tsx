import { Localized } from '@fluent/react';
import parse from 'html-react-parser';
import React, { Fragment, useContext, useLayoutEffect } from 'react';
// @ts-expect-error Working types are unavailable for react-linkify 0.2.2
import Linkify from 'react-linkify';

import type { Entity } from '~/api/entity';
import type { TeamCommentState } from '~/modules/teamcomments';

import { Locale } from '~/context/Locale';
import { FluentAttribute } from './FluentAttribute';
import { Property } from './Property';

import './Metadata.css';
import { MessageEntry, parseEntry } from '~/utils/message';
import { getPlaceholderMap } from '~/utils/message/placeholders';

type Props = {
  entity: Entity;
  teamComments: TeamCommentState;
  navigateToPath: (path: string) => void;
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

function EntityCreatedDate({ dateCreated }: { dateCreated: string }) {
  // Create date and time formatters
  const dateFormatter = new Intl.DateTimeFormat('en-US', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
  const timeFormatter = new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  // Create a Date object from the dateCreated string
  const date = new Date(dateCreated);

  // Format the date and time
  const formattedDate = dateFormatter.format(date);
  const formattedTime = timeFormatter.format(date);

  // Combine the formatted date and time into one string
  const formattedDateTime = `${formattedDate} ${formattedTime}`;

  return (
    <Datum id='entity-created-date' title='CREATED'>
      {formattedDateTime}
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

function SourceReferences({ meta }: { meta: Entity['meta'] }) {
  const refs = [];
  for (let [key, value] of meta) {
    if (key === 'reference') {
      refs.push(
        <li key={value}>
          <span className='title'>#:</span>
          {value}
        </li>,
      );
    }
  }
  return refs.length > 0 ? <ul>{refs}</ul> : null;
}

function SourceExamples({ entry }: { readonly entry: MessageEntry | null }) {
  if (!entry?.value || Array.isArray(entry.value)) return null;
  const phMap = getPlaceholderMap(entry.value);
  if (!phMap) return null;
  const placeholders = Array.from(phMap.values());
  const examples: string[] = [];
  for (const [name, exp] of Object.entries(entry.value.decl)) {
    const example = exp.attr?.example;
    if (typeof example === 'string') {
      const ph = placeholders.find((ph) => ph.$ === name);
      const source = ph?.attr?.source;
      if (typeof source === 'string') {
        examples.push(`${source}: ${example}`);
      }
    }
  }

  return examples.length ? (
    <Datum
      className='placeholder'
      id='placeholder'
      title='PLACEHOLDER EXAMPLES'
    >
      {examples.join(', ')}
    </Datum>
  ) : null;
}

const EntityContext = ({
  entity: { format, key, path, project },
  localeCode,
  navigateToPath,
}: {
  entity: Entity;
  localeCode: string;
  navigateToPath: (path: string) => void;
}) => (
  <Localized id='entitydetails-Metadata--context' attrs={{ title: true }}>
    <Property title='CONTEXT' className='context'>
      {key
        .filter((_, i) => i !== 0 || format !== 'gettext')
        .toReversed()
        .map((k, i) => (
          <Fragment key={i}>
            {k}
            <span className='divider'>&bull;</span>
          </Fragment>
        ))}
      <a
        href={`/${localeCode}/${project.slug}/${path}/`}
        onClick={(ev) => {
          ev.preventDefault();
          navigateToPath(ev.currentTarget.pathname);
        }}
        className='resource-path'
      >
        {path}
      </a>
      <span className='divider'>&bull;</span>
      <a href={`/${localeCode}/${project.slug}/`}>{project.name}</a>
    </Property>
  </Localized>
);

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
  entity,
  navigateToPath,
  teamComments,
}: Props): React.ReactElement {
  const { code } = useContext(Locale);
  const entry = parseEntry(entity.format, entity.original);

  return (
    <div className='metadata'>
      <PinnedComments teamComments={teamComments} />
      <EntityComment comment={entity.comment} />
      <GroupComment comment={entity.group_comment} />
      <ResourceComment comment={entity.resource_comment} key={entity.pk} />
      <FluentAttribute entry={entry} />
      <SourceReferences meta={entity.meta} />
      <SourceExamples entry={entry} />
      <EntityContext
        entity={entity}
        localeCode={code}
        navigateToPath={navigateToPath}
      />
      <EntityCreatedDate dateCreated={entity.date_created} />
    </div>
  );
}
