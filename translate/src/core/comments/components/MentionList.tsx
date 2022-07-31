import { Localized } from '@fluent/react';
import React, { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import type { Range } from 'slate';
import { ReactEditor } from 'slate-react';

import type { MentionUser } from '~/api/user';

type Props = {
  editor: ReactEditor;
  index: number;
  onSelect(user: MentionUser): void;
  suggestedUsers: MentionUser[];
  target: Range;
};

export function MentionList({
  editor,
  index,
  onSelect,
  suggestedUsers,
  target,
}: Props): React.ReactPortal | null {
  const ref = useRef<HTMLDivElement>(null);
  const [scrollPosition, setScrollPosition] = useState(0);

  // Set position of mentions suggestions
  useLayoutEffect(() => {
    try {
      if (ref.current) {
        const range = ReactEditor.toDOMRange(editor, target);
        setMentionListStyle(ref.current, range);
      }
    } catch (error) {
      // https://github.com/mozilla/pontoon/issues/2298
      // toDOMRange may fail on e.g. paste events, as the onChange may be
      // triggered before the DOM is updated. In that case, ignore the error
      // and let the next render fix things if necessary.
    }
  }, [editor, suggestedUsers.length, target, scrollPosition]);

  // Set scroll position values for Translation and Team Comment containers ~
  // This allows for the mention suggestions to stay properly positioned
  // when the container scrolls.
  useEffect(() => {
    const handleScroll = (e: Event) => {
      const element = e.currentTarget as HTMLElement;
      setScrollPosition(element.scrollTop);
    };

    const historyScroll = document.querySelector('#history-list');
    const teamsScroll = document.querySelector('#react-tabs-3');
    if (historyScroll || teamsScroll) {
      historyScroll?.addEventListener('scroll', handleScroll);
      teamsScroll?.addEventListener('scroll', handleScroll);

      return () => {
        historyScroll?.removeEventListener('scroll', handleScroll);
        teamsScroll?.removeEventListener('scroll', handleScroll);
      };
    }
  }, []);

  const setStyleForHover = (ev: React.MouseEvent<HTMLDivElement>) => {
    ev.preventDefault();
    ev.currentTarget.children[index].className = 'mention';
  };

  const removeStyleForHover = (ev: React.MouseEvent<HTMLDivElement>) => {
    ev.preventDefault();
    ev.currentTarget.children[index].className = 'mention active-mention';
  };

  return document.body && suggestedUsers.length > 0
    ? createPortal(
        <div
          ref={ref}
          className='comments-mention-list'
          onMouseEnter={setStyleForHover}
          onMouseLeave={removeStyleForHover}
        >
          {suggestedUsers.map((user, i) => (
            <div
              key={user.name}
              className={i === index ? 'mention active-mention' : 'mention'}
              onMouseDown={(ev) => {
                ev.preventDefault();
                onSelect(user);
              }}
            >
              <Localized
                id='comments-AddComment--mention-avatar-alt'
                attrs={{ alt: true }}
              >
                <span className='user-avatar'>
                  <img
                    src={user.gravatar}
                    alt='User Avatar'
                    width={22}
                    height={22}
                  />
                </span>
              </Localized>
              <span className='name'>{user.name}</span>
            </div>
          ))}
        </div>,
        document.body,
      )
    : null;
}

function setMentionListStyle(el: HTMLDivElement, domRange: globalThis.Range) {
  const rect = domRange.getBoundingClientRect();

  // get team comments element, gain access to its measurements, and verify
  // if it is active
  const teamCommentsEl = document.querySelector('.top');
  const teamCommentsRect = teamCommentsEl?.getBoundingClientRect();
  const teamCommentsActive = teamCommentsEl?.contains(document.activeElement);

  // get translation comments element, gain access to its measurements, and verify
  // if it is active
  const translateCommentsEl = document.querySelector('.history');
  const translateCommentsRect = translateCommentsEl?.getBoundingClientRect();
  const translateCommentsActive = translateCommentsEl?.contains(
    document.activeElement,
  );

  // get editor menu element and find its height to determine when comment editor goes above
  // the editor menu in order to hide suggestions element
  const editorMenuHeight =
    document.querySelector('.editor-menu')?.clientHeight ?? 0;

  // get tab index element and find its height to use when determining if suggestions
  // element overflows the team comments container
  const tabIndexHeight =
    document.querySelector('.react-tabs__tab-list')?.clientHeight ?? 0;

  // get comment editor element and find measurements of values needed to adjust
  // the suggestions element to the correct position
  const commentEditor = document.querySelector(
    '.comments-list .add-comment .comment-editor',
  );
  const ceStyle = commentEditor ? window.getComputedStyle(commentEditor) : null;
  const ceLineHeight = parseInt(ceStyle?.lineHeight ?? '0');
  const ceTopPadding = parseInt(ceStyle?.paddingTop ?? '0');
  const ceBottomPadding = parseInt(ceStyle?.paddingBottom ?? '0');
  const ceSpanHeight =
    document.querySelector<HTMLElement>(
      '.comments-list .add-comment .comment-editor p span',
    )?.offsetHeight ?? 0;

  // add value of comment editor bottom padding and span height to properly position suggestions element
  const setTopAdjustment = ceBottomPadding + ceSpanHeight;

  // add value of comment editor top padding and difference between line height and span height
  // of the top half of the comment editor to correctly size the height of the suggestions
  const suggestionsHeightAdjustment =
    ceTopPadding + (ceLineHeight - ceSpanHeight) / 2;

  let setTop = rect.top + window.pageYOffset + setTopAdjustment;
  let setLeft = rect.left + window.pageXOffset;

  // If suggestions overflow the window or teams container height then adjust the
  // position so they display above the comment
  const suggestionsHeight = el.clientHeight + suggestionsHeightAdjustment;
  const teamCommentsOverflow = !teamCommentsRect
    ? false
    : setTop + el.clientHeight - tabIndexHeight > teamCommentsRect.height;

  if (
    (teamCommentsActive && teamCommentsOverflow) ||
    setTop + suggestionsHeight > window.innerHeight
  ) {
    setTop = rect.top + window.pageYOffset - suggestionsHeight;
  }

  // If suggestions in team comments scroll below or suggestions in translation
  // comments scroll above the next section or overflow the window then hide the suggestions
  if (
    (teamCommentsRect &&
      teamCommentsActive &&
      setTop + suggestionsHeight - editorMenuHeight >
        teamCommentsRect.height) ||
    (translateCommentsRect &&
      translateCommentsActive &&
      (rect.top < translateCommentsRect.top ||
        setTop + suggestionsHeight > window.innerHeight))
  ) {
    el.style.display = 'none';
  } else {
    // If suggestions overflow the window width in team comments or the right side of the
    // translations comments then adjust the position so they display to the left of the mention
    const suggestionsWidth = el.clientWidth;
    const translateCommentsOverflow = !translateCommentsRect
      ? false
      : setLeft + suggestionsWidth > translateCommentsRect.right;

    if (
      setLeft + suggestionsWidth > window.innerWidth ||
      (translateCommentsActive && translateCommentsOverflow)
    ) {
      setLeft = rect.right - suggestionsWidth;
    }

    el.style.display = 'block';
    el.style.top = `${setTop}px`;
    el.style.left = `${setLeft}px`;
  }
}
