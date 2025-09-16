// ESLint Flat Config (ESLint v9+)
// Flat config in CJS (ESLint v9)
const js = require('@eslint/js')
const pluginVue = require('eslint-plugin-vue')

module.exports = [
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.js','**/*.vue'],
    languageOptions: {
      ecmaVersion: 2023,
      sourceType: 'module',
      globals: {
        // Browser environment globals (explicit to silence no-undef for timers & common APIs)
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        fetch: 'readonly',
        console: 'readonly',
        Event: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        setInterval: 'readonly',
        clearInterval: 'readonly'
      }
    },
    rules: {
      'vue/multi-word-component-names': 'off',
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn','error'] }],
      // 降噪: 暂停格式/排列类高噪音规则，后续分阶段再开启
      'vue/html-indent': 'off',
      'vue/max-attributes-per-line': 'off',
      'vue/singleline-html-element-content-newline': 'off',
      'vue/multiline-html-element-content-newline': 'off',
      'vue/html-self-closing': 'off',
      'vue/attributes-order': 'off',
      'vue/no-unused-components': 'warn'
    }
  }
]
