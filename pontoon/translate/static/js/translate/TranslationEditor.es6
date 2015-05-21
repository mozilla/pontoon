import {notify} from './utils.js';


/**
 * Root Component for the entire translation editor.
 */
export default class TranslationEditor extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      loaded: false,
      sidebarOpen: true,  // Temporarily defaults to open for dev.
      entities: [],
      selectedIndex: 0,
    };
  }

  render() {
    return (
      <div id="translation-editor">
        <aside id="sidebar"
               className={classNames('advanced', {open: this.state.sidebarOpen})}
               ref="sidebar">
          <EntityList entities={this.props.entities}
                      project={this.props.project}
                      selectedIndex={this.state.selectedIndex}
                      onSelectEntity={this.selectEntity.bind(this)} />
          <EntityDetails entity={this.selectedEntity}
                         onSelectNextEntity={this.selectNextEntity.bind(this)}
                         onSelectPreviousEntity={this.selectPreviousEntity.bind(this)}
                         onSave={this.saveTranslation.bind(this)} />
        </aside>
      </div>
    );
  }

  get selectedEntity() {
    return this.props.entities[this.state.selectedIndex];
  }

  selectEntity(entityKey) {
    let index = this.props.entities.findIndex((e) => e.pk === entityKey);
    if (index !== -1) {
      this.setState({
        selectedIndex: index,
      });
    }
  }

  saveTranslation(string) {
    this.props.onSaveTranslation(this.selectedEntity, string);
  }

  selectNextEntity(e) {
    e.preventDefault();
    if (this.state.selectedIndex < this.props.entities.length - 1) {
      this.setState((props, state) => ({
        selectedIndex: state.selectedIndex + 1,
      }));
    }
  }

  selectPreviousEntity(e) {
    e.preventDefault();
    if (this.state.selectedIndex > 0) {
      this.setState({
        selectedIndex: this.state.selectedIndex - 1,
      });
    }
  }

  toggleSidebar() {
    this.setState((state, props) => ({
      sidebarOpen: !state.sidebarOpen
    }));
  }
}


/**
 * List of entities that appears in the sidebar.
 */
class EntityList extends React.Component {
  render() {
    let listBody = <h3 className="no-match"><div>ఠ_ఠ</div>No results</h3>;

    if (this.props.entities.length > 0) {
      let entities = [];
      for (let k = 0; k < this.props.entities.length; k++) {
        let entity = this.props.entities[k];
        let selected = k == this.props.selectedIndex;

        entities.push(
          <EntityItem key={entity.pk}
                      entity={entity}
                      selected={selected}
                      onSelectEntity={this.props.onSelectEntity} />
        );
      }

      listBody = (
        <div className="wrapper">
          <ul className="editables">
            {entities}
          </ul>
          {this.props.project.url
            ? <h2 id="not-on-page">Not on the current page</h2>
            : null}
          <ul className="uneditables"></ul>
        </div>
      );
    }

    return (
      <div id="entitylist">
        <EntitySearch />
        {listBody}
      </div>
    );
  }
}


/**
 * Search input above the list of entities in the sidebar.
 */
class EntitySearch extends React.Component {
  render() {
    return (
      <div className="search-wrapper clearfix">
        <div className="icon fa fa-search"></div>
        <input id="search" type="search" placeholder="Search" />
        <div id="filter" className="select">
          <div className="button selector all">
            <span className="status fa"></span>
            <span className="title">All</span>
          </div>
          <div className="menu">
            <ul>
              <li className="all"><span className="status fa"></span>All</li>
              <li className="untranslated"><span className="status fa"></span>Untranslated</li>
              <li className="fuzzy"><span className="status fa"></span>Needs work</li>
              <li className="translated"><span className="status fa"></span>Unapproved</li>
              <li className="approved"><span className="status fa"></span>Approved</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }
}


/**
 * Individual entity in the sidebar list.
 */
class EntityItem extends React.Component {
  render() {
    let entity = this.props.entity;
    let translationString = '';
    if (entity.approvedTranslation) {
      translationString = entity.approvedTranslation.string;
    } else if (entity.translations.length > 0) {
      translationString = entity.translations[0].string;
    }

    let liClassname = classNames('entity', 'limited', entity.status, {
      'hovered': this.props.selected
    })
    return (
      <li className={liClassname}
          onClick={this.selectEntity.bind(this)}>
        <span className="status fa"></span>
        <p className="string-wrapper">
          <span className="source-string">{entity.marked}</span>
          <span className="translation-string">{translationString}</span>
        </p>
        <span className="arrow fa fa-chevron-right fa-lg"></span>
      </li>
    );
  }

  selectEntity() {
    this.props.onSelectEntity(this.props.entity.pk);
  }
}


/**
 * Detailed view for an individual Entity.
 */
class EntityDetails extends React.Component {
  render() {
    let entity = this.props.entity;

    return (
      <div id="editor">
        <div id="drag-1" draggable="true"></div>

        <EntityDetailsNav onSelectNextEntity={this.props.onSelectNextEntity}
                         onSelectPreviousEntity={this.props.onSelectPreviousEntity} />
        <EntitySourcePane entity={entity} />
        <EntityEditor entity={entity} onSave={this.props.onSave}/>
      </div>
    );
  }
}


class EntityDetailsNav extends React.Component {
  render() {
    return (
      <div id="topbar" className="clearfix">
        <a id="back" href="#back">
          <span className="fa fa-chevron-left fa-lg"></span>
          Back to list
        </a>
        <a id="next" href="#next" onClick={this.props.onSelectNextEntity}>
          <span className="fa fa-chevron-down fa-lg"></span>
          Next
        </a>
        <a id="previous" href="#previous" onClick={this.props.onSelectPreviousEntity}>
          <span className="fa fa-chevron-up fa-lg"></span>
          Previous
        </a>
      </div>
    );
  }
}


class EntitySourcePane extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      showAll: false,
    };
  }

  render() {
    let metadata = [];
    let entity = this.props.entity;

    if (entity.comment) {
      metadata.push(<span id="comment" key="comment">{entity.comment}</span>);
    }

    if (entity.path || entity.key) {
      if (this.state.showAll) {
        metadata.push(
          <a href="#"
             className="details"
             key="showHide"
             onClick={this.showLessMetadata.bind(this)}>
            Less details
          </a>
        );
      } else {
        metadata.push(
          <a href="#"
             className="details"
             key="showHide"
             onClick={this.showMoreMetadata.bind(this)}>
            More details
          </a>
        );
      }
    }

    if (entity.path) {
      metadata.push(<span key="path">{entity.path}</span>);
    }

    if (entity.key) {
      metadata.push(<span key="key">Key: {entity.key}</span>);
    }

    return (
      <div id="source-pane">
        <p id="metadata" className={classNames({'show-all': this.state.showAll})}>
          {metadata}
        </p>
        <p id="original">{entity.marked}</p>
      </div>
    )
  }

  showMoreMetadata(e) {
    e.preventDefault();
    this.setState({
      'showAll': true,
    });
  }

  showLessMetadata(e) {
    e.preventDefault();
    this.setState({
      'showAll': false,
    });
  }
}


class EntityEditor extends React.Component {
  constructor(props ) {
    super(props);
    this.state = {
      'inputValue': '',
    };
  }

  render() {
    return (
      <div className="entity-editor">
        <textarea id="translation"
                  placeholder="Enter translation"
                  value={this.state.inputValue}
                  onChange={this.handleChange.bind(this)} />

        <menu className="editor-buttons">
          <div id="translation-length">
            {this.state.inputValue.length} / {this.props.entity.string.length}
          </div>
          <button onClick={this.handleCopy.bind(this)}>Copy</button>
          <button onClick={this.handleClear.bind(this)}>Clear</button>
          <button className="save" onClick={this.handleSave.bind(this)}>Save</button>
        </menu>
      </div>
    )
  }

  componentWillReceiveProps(nextProps) {
    let entity = nextProps.entity;
    this.setState({
      inputValue: entity.approvedTranslation ? entity.approvedTranslation.string : ''
    });
  }

  handleChange(e) {
    this.setState({
      inputValue: e.target.value,
    });
  }

  handleCopy() {
    this.setState({inputValue: this.props.entity.string});
  }

  handleClear() {
    this.setState({inputValue: ''});
  }

  handleSave() {
    this.props.onSave(this.state.inputValue);
  }
}
