import * as path from 'path';
import 'tsarch/dist/jest';
import { filesOfProject } from 'tsarch';
import { extractGraph } from 'tsarch/dist/src/common/extraction/extractGraph';
import { projectEdges } from 'tsarch/dist/src/common/projection/projectEdges';
import { gatherCycleViolations } from 'tsarch/dist/src/files/assertion/freeOfCycles';
import type { Violation } from 'tsarch/dist/src/common/assertion/violation';

class HighLevelChecker {
    public async check(): Promise<Violation> {
        const graph = await extractGraph();
        function modder(filepath) {
            return path.relative('src', path.dirname(filepath));
        }
        const projected = projectEdges(graph, (edge) => {
            if (edge.external) {
                return;
            }
            const labeled = {
                sourceLabel: modder(edge.source),
                targetLabel: modder(edge.target),
            };
            if (labeled.sourceLabel === labeled.targetLabel) {
                return;
            }
            return labeled;
        });
        return gatherCycleViolations(projected, []);
    }
}

describe('architecture', () => {
    jest.setTimeout(60000);

    it('core should not depend on components', async () => {
        const rule = filesOfProject()
            .inFolder('core')
            .shouldNot()
            .dependOnFiles()
            .inFolder('modules');
        await expect(rule).toPassAsync();
    });

    it('high-level structure should not have circular dependencies', async () => {
        const rule = new HighLevelChecker();
        await expect(rule).toPassAsync();
    });
});
