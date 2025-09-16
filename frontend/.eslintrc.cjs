/**
 * 最小 ESLint 配置 (观测阶段)
 * 可逐步扩展 import/order / prettier 等。
 */
module.exports = {
  root: true,
  env: { browser: true, node: true, es2023: true },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended'
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 2023,
    sourceType: 'module'
  },
  rules: {
    'vue/multi-word-component-names': 0,
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-console': ['warn', { allow: ['warn', 'error'] }]
  }
};
