# Content Processing Modules

Modular architecture for content source processing.

```
src/modules/
├── shared/       # Types, constants, utilities
├── website/      # ✅ Implemented — Readability + keyword/LLM analysis
├── youtube/      # 📋 Placeholder
└── instagram/    # 📋 Placeholder
```

All processors implement the `ContentProcessor` interface from `shared/types.ts`.

## Adding a New Source

```typescript
import type { ContentProcessor } from '../shared/types'

class MyProcessor implements ContentProcessor {
  sourceType = 'mysource'
  canHandle(url: string) { return url.includes('mysource.com') }
  async extract(url: string) { /* fetch + parse */ }
  async analyze(source: ContentSource) { /* LLM or keyword analysis */ }
}
```
