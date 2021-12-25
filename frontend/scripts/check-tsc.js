/* eslint no-console: "off" */
/* eslint @typescript-eslint/no-var-requires: "off" */
/* global __dirname */
const path = require('path');
const ts = require('typescript');

class DefaultMap extends Map {
    constructor(createDefault) {
        super();
        this.createDefault = createDefault;
    }
    get(key) {
        if (!this.has(key)) {
            this.set(key, this.createDefault());
        }
        return super.get(key);
    }
}

const reporter = ts.createDiagnosticReporter(ts.sys, true);

const loadCompilerConfig = () => {
    const config = ts.readConfigFile('tsconfig.json', ts.sys.readFile).config;
    const tmp = ts.convertCompilerOptionsFromJson(config.compilerOptions, '');
    if (tmp.errors.length > 0) throw new Error('...');
    return tmp.options;
};

const getDiagnostics = (defaultOpts, opts = {}) => {
    const program = ts.createProgram(
        ['src/index.tsx', 'src/test/store.tsx', 'src/test/utils.ts'],
        { ...defaultOpts, ...opts },
    );
    const result = program.emit();
    return [...result.diagnostics, ...ts.getPreEmitDiagnostics(program)];
};

const flattenMessages = (diagnostic) => {
    if (typeof diagnostic.messageText === 'string') {
        return [{ message: diagnostic.messageText, code: diagnostic.code }];
    }
    const msgChain = diagnostic.messageText;
    let messages = [{ message: msgChain.messageText, code: msgChain.code }];
    for (const child of msgChain.next) {
        messages = [...messages, ...flattenMessages(child)];
    }
    return messages;
};

function* generateAnnotations(maps) {
    const filePaths = Array.from(maps.keys());
    filePaths.sort();
    for (const filePath of filePaths) {
        const fileData = maps.get(filePath);
        const starts = Array.from(fileData.keys());
        starts.sort();
        for (const start of starts) {
            for (const messages of fileData.get(start).values()) {
                yield {
                    path: filePath,
                    start_line: messages.startPos.line + 1,
                    end_line: messages.endPos.line + 1,
                    start_column: messages.startPos.character + 1,
                    end_column: messages.endPos.character + 1,
                    annotation_level: 'notice',
                    message: messages.messages.map((m) => m.message).join('\n'),
                    title: `${messages.messages[0].code}`,
                };
            }
        }
    }
}

const flags = ['noImplicitAny', 'strictNullChecks', 'strict'];

async function run() {
    const defaultOpts = loadCompilerConfig();
    for (const flag of flags) {
        console.log(`::group::${flag}`);
        const codes = new DefaultMap(() => new DefaultMap(() => new Map()));
        const diags = getDiagnostics(defaultOpts, { [flag]: true });
        for (const d of diags) {
            reporter(d);
            const { fileName } = d.file;
            const relPath = path.relative(
                path.resolve(__dirname, '../..'),
                fileName,
            );
            const messages = flattenMessages(d);
            const startPos = d.file.getLineAndCharacterOfPosition(d.start);
            const endPos = d.file.getLineAndCharacterOfPosition(
                d.start + d.length,
            );
            codes.get(relPath).get(d.start).set(d.length, {
                startPos,
                endPos,
                messages,
            });
        }
        console.log('::endgroup::');
        const annotations = Array.from(generateAnnotations(codes));
        console.log(`::group::${flag}-data`);
        console.log(
            `::set-output name=${flag}::${JSON.stringify(annotations)}`,
        );
        console.log('::endgroup::');
    }
}

run();
