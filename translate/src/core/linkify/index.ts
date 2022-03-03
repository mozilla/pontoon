import LinkifyIt from 'linkify-it';
import tlds from 'tlds';

/**
 * Wrap linkify library to express the expected functionality
 * in a central place, paired with integration tests.
 */
export { default as Linkify } from 'react-linkify';

// Create and configure a URLs matcher.
const linkify = new LinkifyIt();
linkify.tlds(tlds);

export function getImageURLs(source: string, locale: string) {
  const matches = linkify.match(source);
  if (!matches) {
    return [];
  }
  return matches
    .filter((match) => /(https?:\/\/.*\.(?:png|jpg))/im.test(match.url))
    .map((match) => match.url.replace(/en-US\//gi, locale + '/'));
}
