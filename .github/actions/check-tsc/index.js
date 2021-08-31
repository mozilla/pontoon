/* eslint no-console: "off" */
const { promisify } = require('util');
const { exec } = require('child_process');

async function run() {
    console.log('::group::tsc');
    let errors = '0';
    const run = process.env['INPUT_RUN'] || 'yarn types --pretty ';
    const cwd = process.env['INPUT_WORKING-DIRECTORY'] || 'frontend';
    let stdout, stderr;
    try {
        ({ stdout, stderr } = await asyncExec(run, {
            cwd,
        }));
    } catch (failed_proc) {
        ({ stdout, stderr } = failed_proc);
    }
    console.log(stdout);
    console.log(stderr);
    const m = /Found ([0-9]+) errors\./.exec(stdout);
    if (m) {
        errors = m[1];
    }
    console.log('::endgroup::');
    console.log(`\nFound ${errors} errors.\n`);
    console.log(`::set-output name=errors::${errors}`);
}

const asyncExec = promisify(exec);

run();
