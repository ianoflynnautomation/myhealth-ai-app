// ESLint covers what oxlint can't: type-aware typescript-eslint rules and React Compiler-aware hooks rules.
// eslint-plugin-oxlint (last) turns off every rule oxlint already enforces.
import js from '@eslint/js'
import prettier from 'eslint-config-prettier'
import oxlint from 'eslint-plugin-oxlint'
import reactHooks from 'eslint-plugin-react-hooks'
import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'
import tseslint from 'typescript-eslint'

export default defineConfig([
  globalIgnores(['dist', 'coverage']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.strictTypeChecked,
      tseslint.configs.stylisticTypeChecked,
      reactHooks.configs.flat['recommended-latest'],
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: {
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    rules: {
      '@typescript-eslint/restrict-template-expressions': [
        'error',
        { allowNumber: true },
      ],
    },
  },
  {
    // Vendored shadcn/ui components: keep them as generated.
    files: ['src/components/ui/**'],
    extends: [tseslint.configs.disableTypeChecked],
  },
  {
    files: ['**/*.js'],
    extends: [js.configs.recommended],
    languageOptions: { globals: globals.node },
  },
  prettier,
  ...oxlint.buildFromOxlintConfigFile('./.oxlintrc.json'),
])
