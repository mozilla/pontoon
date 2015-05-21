/**
 * Component for selecting the project you want to translate.
 */
export default class TranslationSelector extends React.Component {
  render() {
    return (
      <div className="selector">
        <ProjectSelector currentProject={this.props.currentProject}
                         projects={this.props.projects} />
      </div>
    );
  }
}


class ProjectSelector extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      showSearch: false
    };
  }

  render() {
    let projects = this.props.projects.map((project) => {
      return <ProjectListItem project={project} terms={project.name} />;
    });
    let search = (
      <InstantSearchList getSearchTerms={(project) => project.props.terms}>
        {projects}
      </InstantSearchList>
    );

    return (
      <div className={classNames('project', 'select', {opened: this.state.showSearch})}>
        <div className="button breadcrumbs selector"
             onClick={this.toggleSearch.bind(this)}>
          <span className="title noselect">{this.props.currentProject.name}</span>
          {this.state.showSearch ? search : ''}
        </div>
      </div>
    );
  }

  toggleSearch() {
    this.setState((state, props) => ({
      showSearch: !state.showSearch
    }));
  }
}


class ProjectListItem extends React.Component {
  render() {
    let project = this.props.project;
    return (
      <div className="project">
        <span className="name">{project.name}</span>
        <span className="url">{project.url}</span>
      </div>
    );
  }
}


class InstantSearchList extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      query: ''
    };
  }

  render() {
    // Wrap children in InstantSearchListItems and hide ones that don't
    // match.
    let anyMatched = false;
    let getSearchTerms = this.props.getSearchTerms;
    let children = React.Children.map(this.props.children, (child) => {
      if (!child) {
        return;
      }

      let searchTerms = getSearchTerms(child).toLowerCase();
      let query = this.state.query.toLowerCase();
      let matched = query === '' || searchTerms.indexOf(query) !== -1;

      // Track if at least one match was made so we can show a message
      // if no matches were made.
      anyMatched = anyMatched || matched;

      return (
        <InstantSearchListItem visible={matched}>
          {child}
        </InstantSearchListItem>
      );
    });

    return (
      <div className="search-list menu">
        <div className="search-wrapper clearfix">
          <div className="icon fa fa-search"></div>
          <input ref="search"
                 type="search"
                 autoComplete="off"
                 autoFocus
                 value={this.state.query}
                 onChange={this.handleChange.bind(this)} />
        </div>
        <ul>
          {!anyMatched ? <li className="no-match">No results</li> : ''}
          {children}
        </ul>
      </div>
    );
  }

  handleChange() {
    let query = React.findDOMNode(this.refs.search).value;
    this.setState({query: query});
  }
}


class InstantSearchListItem extends React.Component {
  render() {
    return (
      <li className={classNames('clearfix', {hidden: !this.props.visible})}>
        {this.props.children}
      </li>
    );
  }
}
