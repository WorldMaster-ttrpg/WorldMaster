import { nodeResolve } from '@rollup/plugin-node-resolve';

export default {
	input: 'out-tsc/ts/main.mjs',
	output: {
		file: 'static/js/bundle.js',
	},
	plugins: [nodeResolve()],
};
