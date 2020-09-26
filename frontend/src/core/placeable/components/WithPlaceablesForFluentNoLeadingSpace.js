/* @flow */

import createMarker from 'react-content-marker';

import './WithPlaceables.css';

import { rules } from './WithPlaceables';
import { getRulesWithFluent } from './WithPlaceablesForFluent';
import { getRulesWithoutLeadingSpace } from './WithPlaceablesNoLeadingSpace';

/**
 * Component that marks placeables in a string. Same as WithPlaceablesForFluent
 * but without some space parsers.
 *
 * See ./WithPlaceablesNoLeadingSpace.js for documentation.
 */
const WithPlaceablesForFluentNoLeadingSpace = createMarker(
    getRulesWithFluent(getRulesWithoutLeadingSpace(rules)),
);

export default WithPlaceablesForFluentNoLeadingSpace;
