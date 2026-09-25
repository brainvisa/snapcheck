# Plan P1 - Contrat front/back typé: Changements appliqués

## Objectif
Générer automatiquement le client API typé à partir de la spécification OpenAPI, éliminant la dérive entre le front et le back.

## Changements effectués

### 1. Configuration TypeScript (NOUVEAU)
**Fichiers créés**:
- `tsconfig.json` - Configuration stricte TypeScript
- `tsconfig.node.json` - Configuration pour vite.config.ts

**Changements**:
- ✅ Activation du mode strict (`"strict": true`)
- ✅ Alias pour `@lepton/api` pointant vers `src/api/generated`
- ✅ Path mapping pour les imports résolvables

### 2. Package.json (MIS À JOUR)

**Dépendances supprimées**:
- ❌ `openapi-typescript-codegen` (maintainability faible)

**Dépendances ajoutées**:
- ✅ `@hey-api/openapi-ts@^0.48.0` - Générateur de client moderne
- ✅ Support de TanStack React Query via plugin

**Scripts ajoutés**:
```json
"typecheck": "tsc --noEmit"     // Vérification TypeScript
"build": "tsc && vite build"     // Build TypeScript + bundle
"build_api": "..."               // Génération du client
```

### 3. Vite Configuration (MIS À JOUR)

**État de transition** (P1 → P2):
- ✅ `@lepton/api-client` → stubs existants (compatible avec code actuel)
- ✅ `@lepton/api` → dossier généré (prêt pour P2)

```typescript
alias: {
  '@lepton/core': path.resolve(..., 'node_modules/@lepton/core'),
  '@lepton/api-client': path.resolve(..., 'snapcheck-front/src/api/types.ts'),
  '@lepton/api': path.resolve(..., 'src/api/generated'),
}
```

### 4. Scripts d'automatisation (NOUVEAUX)

**`scripts/export_openapi.py`**:
- Exporte la spécification OpenAPI depuis FastAPI
- Génère `openapi.json`

**`scripts/generate_api_client.sh`**:
- Utilise `@hey-api/openapi-ts` pour générer le client
- Crée types + React Query hooks + client axios

## Workflow d'utilisation

### Phase 1 (MAINTENANT) - Configuration
```bash
npm install  # Installer les dépendances
npm run typecheck  # Vérifier TypeScript
```

### Phase 2 (APRÈS CHANGEMENTS API) - Génération
```bash
python scripts/export_openapi.py  # Exporte le schéma OpenAPI
bash scripts/generate_api_client.sh  # Génère le client
npm run typecheck  # Vérifie la compilation
```

### Phase 3 (P2) - Migration progressive
Remplacer progressivement les imports:
```typescript
// Avant (stubs):
import { ObjectsService } from '@lepton/api-client'

// Après (généré):
import { useGetObjects } from '@lepton/api'
```

## Avantages

✅ **Contrat unique source** - OpenAPI est la vérité (backend)
✅ **Génération automatique** - Pas de stubs manuels
✅ **Types complets** - Requêtes, réponses, modèles
✅ **React Query natif** - Hooks générés automatiquement
✅ **Maintenance centralisée** - Un seul point de vérité
✅ **Compilation stricte** - TypeScript detecte les erreurs

## Prochaines étapes

1. **Exécuter P1**:
   ```bash
   npm install  # Installer @hey-api/openapi-ts
   npm run typecheck  # Vérifier la compilation
   ```

2. **Préparation pour P2**:
   - Exporter OpenAPI du serveur
   - Générer le client
   - Tester les types générés

3. **P2 - Migration**:
   - Intégrer les queries dans SessionContext
   - Remplacer les imports progressivement
   - Valider avec tests

## Important ⚠️

- `src/api/generated/` n'existe pas encore (créé par script)
- Les stubs `@lepton/api-client` restent disponibles pendant la transition
- N'est pas obligatoire de migrer tout d'un coup (peuvent coexister)
