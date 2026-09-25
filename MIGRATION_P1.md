# Migration P1 - Utilisation du client généré

## État actuel ✅

Le client API a été généré dans `src/api/generated/`:
- ✅ `services.gen.ts` - Services HTTP typés (avec workaround pour le bug `new`)
- ✅ `types.gen.ts` - Tous les types TypeScript
- ✅ `schemas.gen.ts` - Schémas JSON
- ✅ `core/` - Client axios et infrastructure

## Utilisation

### Services générés

```typescript
import { ObjectsService, type CreateObjectResponse } from '@lepton/api'

// Les services sont des fonctions typées
const response: CreateObjectResponse = await ObjectsService.newObject({
  path: '/tmp/my_snap'
})
```

### Types générés

```typescript
import type { SnapModel, BoardModel, RatingModel } from '@lepton/api'

function renderSnap(snap: SnapModel) {
  // Complètement typé avec autocomplete
  return snap.title
}
```

## Migration progressive

### Phase 1: Imports de types (LOW RISK)
Remplacer les imports de types de `@lepton/api-client` vers `@lepton/api`:

```typescript
// Avant:
import type { RatingModel } from '@lepton/api-client'

// Après:
import type { RatingModel } from '@lepton/api'
```

### Phase 2: Services HTTP (NEEDS TESTING)
Remplacer les appels de service:

```typescript
// Avant (stubs - ne fonctionnent pas):
import { ObjectsService } from '@lepton/api-client'
ObjectsService.getObjects()

// Après (généré - fonctionne):
import { ObjectsService } from '@lepton/api'
const result = await ObjectsService.getObjects()
```

## Workarounds nécessaires

1. **Fonction `newObject` nommée incorrectement**
   - La route `/objects/new` génère une fonction exportée `new` (mot réservé)
   - Workaround: Renommé en `newObject` dans services.gen.ts
   - TODO: Renommer la route backend à `/objects/create` pour éviter ce problème

## Prochaines étapes

1. **Migrer progressivement les imports de types**
   - Remplacer `@lepton/api-client` → `@lepton/api` pour les types
   - Pas de changement de comportement, juste des imports

2. **Intégrer avec React Query (P2)**
   - Créer des hooks React Query custom autour des services
   - Utiliser dans SessionContext

3. **Corriger le backend**
   - Renommer `/objects/new` → `/objects/create` pour éviter le mot réservé
   - Régénérer le client

## Test

```bash
npm run typecheck  # Compile avec types générés
npm run build_api  # Régénère le client si openapi.json change
```
