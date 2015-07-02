/**
 * A project that contains many entities to translate.
 */
export class Project {
  constructor(data) {
    $.extend(this, data);
  }

  static fetchAll() {
    return $.get('/projects/').then((projects) => {
      return projects.map((data) => new Project(data));
    });
  }
}

/**
 * A single string to be translated.
 */
export class Entity {
  constructor(data) {
    $.extend(this, data);
  }

  /**
   * Return the first approved translation in this.translations, or null
   * if there are none.
   */
  get approvedTranslation() {
    for (let translation of this.translations) {
      if (translation.approved) {
        return translation;
      }
    }

    return null;
  }

  /**
   * Return the current translation status.
   */
  get status() {
    if (this.approvedTranslation) {
      return 'approved';
    } else if (this.translations.some((t) => t.fuzzy)) {
      return 'fuzzy'
    } else if (this.translations.length > 0) {
      return 'translated';
    } else {
      return '';
    }
  }

  updateTranslation(string, localeCode) {
    let url = `/entities/${this.pk}/translations/${localeCode}/`;
    return $.post(url, {string}).then((translations) => {
      return $.extend(this, {translations})
    });
  }

  /**
   * Fetch all the entities for the given project and locale.
   */
  static fetchAll(projectSlug, localeCode) {
    let url = `/projects/${projectSlug}/locales/${localeCode}/entities`;
    return $.get(url).then((entities) => {
      return entities.map((data) => new Entity(data));
    });
  }
}
