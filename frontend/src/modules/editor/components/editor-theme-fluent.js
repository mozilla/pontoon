/* global ace */

ace.define(
    "ace/theme/fluent",
    ["require", "exports", "module", "ace/lib/dom"],
    theme
);

function theme(acequire, exports) {
    exports.isDark = false;
    exports.cssClass = "ace-fluent";


    exports.cssText = `
        .ace-fluent {
            background-color: #f7f7f7;
            color: #222;
        }

        .ace-fluent .ace_cursor {
            color: #222;
        }

        .ace-fluent .ace_gutter {
            background: #e8e8e8;
            color: #aaa;
        }

        .ace-fluent .ace_print-margin {
            width: 1px;
            background: #e8e8e8;
        }

        .ace-fluent .ace_invisible {
            color: #bfbfbf
        }

        .ace-fluent .ace_indent-guide {
            background: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAACCAYAAACZgbYnAAAAE0lEQVQImWP4////f4bLly//BwAmVgd1/w11/gAAAABJRU5ErkJggg==") right repeat-y;
        }

        .ace-fluent .ace_comment {
            color: #999;
            font-style: italic;
        }

        /* Message and Term definitions */
        .ace-fluent .ace_entity {
            font-weight: bold;
        }

        /* TextElements */
        .ace-fluent .ace_string.ace_unquoted {
            color: #1a1aa6;
        }

        /* MessageReferences and TermReferences */
        .ace-fluent .ace_variable {
            color: #08c;
        }

        /* VariableReferences */
        .ace-fluent .ace_parameter {
            color: #930f80;
        }

        .ace-fluent .ace_keyword,
        .ace-fluent .ace_function {
            font-weight: normal;
            color: #930f80;
        }

        /* Literals */
        .ace-fluent .ace_constant,
        .ace-fluent .ace_string.ace_quoted {
            color: green;
        }

        /* Parens and commas */
        .ace-fluent .ace_paren,
        .ace-fluent .ace_punctuation {
            color: #08c;
        }

        .ace-fluent .ace_invalid {
            background-color: rgba(255, 0, 0, 0.1);
            color: red;
        }

        .ace-fluent.ace_focus .ace_marker-layer .ace_active-line {
            background: rgb(255, 255, 204);
        }

        .ace-fluent .ace_marker-layer .ace_active-line {
            background: rgb(245, 245, 245);
        }

        .ace-fluent .ace_marker-layer .ace_selection {
            background: rgb(181, 213, 255);
        }

        .ace-fluent.ace_multiselect .ace_selection.ace_start {
            box-shadow: 0 0 3px 0px white;
        }

        .ace-fluent.ace_nobold .ace_line > span {
            font-weight: normal !important;
        }

        .ace-fluent .ace_marker-layer .ace_step {
            background: rgb(252, 255, 0);
        }

        .ace-fluent .ace_marker-layer .ace_stack {
            background: rgb(164, 229, 101);
        }

        .ace-fluent .ace_marker-layer .ace_bracket {
            margin: -1px 0 0 -1px;
            border: 1px solid rgb(192, 192, 192);
        }

        .ace-fluent .ace_gutter-active-line {
            background-color : rgba(0, 0, 0, 0.07);
        }

        .ace-fluent .ace_marker-layer .ace_selected-word {
            background: rgb(250, 250, 255);
            border: 1px solid rgb(200, 200, 250);
        }
    `;

    const dom = acequire("../lib/dom");
    dom.importCssString(exports.cssText, exports.cssClass);
}
