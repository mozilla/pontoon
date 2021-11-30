import * as React from 'react';

import './Entity.css';

import { TranslationProxy } from 'core/translation';
import { Localized } from '@fluent/react';

import type { Entity as EntityType } from 'core/api';
import type { Locale } from 'core/locale';
import type { NavigationParams } from 'core/navigation';

type Props = {
    checkedForBatchEditing: boolean;
    toggleForBatchEditing: (...args: Array<any>) => any;
    entity: EntityType;
    isReadOnlyEditor: boolean;
    isTranslator: boolean;
    locale: Locale;
    selected: boolean;
    selectEntity: (...args: Array<any>) => any;
    getSiblingEntities: Function;
    parameters: NavigationParams;
};

type State = {
    areSiblingsActive: Boolean;
};

/**
 * Displays a single Entity as a list element.
 *
 * The format of this element is: "[Status] Source (Translation)"
 *
 * "Status" is the current status of the translation. Can be:
 *   - "errors": one of the plural forms has errors and is approved or fuzzy
 *   - "warnings": one of the plural forms has warnings and is approved or fuzzy
 *   - "approved": all plural forms are approved and don't have errors or warnings
 *   - "fuzzy": all plural forms are fuzzy and don't have errors or warnings
 *   - "partial": some plural forms have either approved or fuzzy translations, but not all
 *   - "missing": none of the plural forms have an approved or fuzzy translation
 *
 * "Source" is the original string from the project. Usually it's the en-US string.
 *
 * "Translation" is the current "best" translation. It shows either the approved
 * translation, or the fuzzy translation, or the last suggested translation.
 */
export default class Entity extends React.Component<Props, State> {
    constructor(props) {
        super(props);
        this.state = { areSiblingsActive: false };
    }
    get status(): string {
        const translations = this.props.entity.translation;
        let approved = 0;
        let fuzzy = 0;
        let errors = 0;
        let warnings = 0;

        translations.forEach(function (translation) {
            if (
                translation.errors.length &&
                (translation.approved || translation.fuzzy)
            ) {
                errors++;
            } else if (
                translation.warnings.length &&
                (translation.approved || translation.fuzzy)
            ) {
                warnings++;
            } else if (translation.approved) {
                approved++;
            } else if (translation.fuzzy) {
                fuzzy++;
            }
        });

        if (errors) {
            return 'errors';
        }
        if (warnings) {
            return 'warnings';
        }
        if (approved === translations.length) {
            return 'approved';
        }
        if (fuzzy === translations.length) {
            return 'fuzzy';
        }
        if (approved > 0 || fuzzy > 0) {
            return 'partial';
        }
        return 'missing';
    }

    selectEntity: (e: React.MouseEvent<HTMLLIElement>) => null | void = (
        e: React.MouseEvent<HTMLLIElement>,
    ) => {
        if (
            e.target instanceof HTMLElement &&
            e.target.classList.contains('status')
        ) {
            return null;
        }
        this.props.selectEntity(this.props.entity);
    };

    getSiblingEntities: (e: React.MouseEvent<HTMLButtonElement>) => void = (
        e: React.MouseEvent<HTMLButtonElement>,
    ) => {
        e.stopPropagation();
        this.props.getSiblingEntities(this.props.entity.pk);
        this.setState({ areSiblingsActive: true });
    };

    toggleForBatchEditing: (e: React.MouseEvent<HTMLSpanElement>) => void = (
        e: React.MouseEvent<HTMLSpanElement>,
    ) => {
        const { entity, isReadOnlyEditor, isTranslator } = this.props;

        if (isTranslator && !isReadOnlyEditor) {
            e.stopPropagation();
            this.props.toggleForBatchEditing(entity.pk, e.shiftKey);
        }
    };

    areFiltersApplied: () => boolean = () => {
        const parameters = this.props.parameters;
        if (
            parameters.status != null ||
            parameters.extra != null ||
            parameters.tag != null ||
            parameters.time != null ||
            parameters.author != null
        ) {
            return true;
        }
        return false;
    };

    showSiblingEntitiesButton: () => boolean = () => {
        const isSearched = this.props.parameters.search;
        const areFiltersApplied = this.areFiltersApplied();
        const areSiblingsActive = !this.state.areSiblingsActive;

        return (isSearched || areFiltersApplied) && areSiblingsActive;
    };

    render(): React.ReactElement<'li'> {
        const {
            checkedForBatchEditing,
            entity,
            isReadOnlyEditor,
            isTranslator,
            locale,
            selected,
            parameters,
        } = this.props;

        const classSelected = selected ? 'selected' : '';

        const classBatchEditable =
            isTranslator && !isReadOnlyEditor ? 'batch-editable' : '';

        const classChecked = checkedForBatchEditing ? 'checked' : '';

        const classSibling = entity.isSibling ? 'sibling' : '';
        return (
            <li
                className={`entity ${this.status} ${classSelected} ${classBatchEditable} ${classChecked} ${classSibling}`}
                onClick={this.selectEntity}
            >
                <span
                    className='status fa'
                    onClick={this.toggleForBatchEditing}
                />
                {classSelected && !classSibling ? (
                    <div>
                        {this.showSiblingEntitiesButton() && (
                            <Localized id='entitieslist-Entity--sibling-strings-title'>
                                <i
                                    className={
                                        'sibling-entities-icon fas fa-expand-arrows-alt'
                                    }
                                    title='Click to reveal sibling strings'
                                    onClick={this.getSiblingEntities}
                                ></i>
                            </Localized>
                        )}
                    </div>
                ) : null}
                <div>
                    <p className='source-string'>
                        <TranslationProxy
                            content={entity.original}
                            format={entity.format}
                            search={parameters.search}
                        />
                    </p>
                    <p
                        className='translation-string'
                        dir={locale.direction}
                        lang={locale.code}
                        data-script={locale.script}
                    >
                        <TranslationProxy
                            content={entity.translation[0].string}
                            format={entity.format}
                            search={parameters.search}
                        />
                    </p>
                </div>
            </li>
        );
    }
}
