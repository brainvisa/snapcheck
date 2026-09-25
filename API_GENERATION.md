# API Client Generation - Guide P1

## Vue d'ensemble

Le contrat front/back est maintenant **généré automatiquement** à partir de la spécification OpenAPI du serveur FastAPI.

**Avant (P0)**: Stubs manuels → dérive API → 404 silencieux
**Après (P1)**: Spécification OpenAPI → Génération automatique → Types stricts

## Workflow

### 1. Démarrer le serveur
```bash
python -m snapserve
```

### 2. Exporter la spécification OpenAPI
```bash
cd snapcheck
python scripts/export_openapi.py
```

Cela crée `openapi.json` avec tous les endpoints, paramètres et types.

### 3. Générer le client API typé
```bash
npm install  # Si pas déjà fait
bash scripts/generate_api_client.sh
```

Cela génère `src/api/generated/` avec:
- Types TypeScript pour toutes les requêtes/réponses
- Mutations et queries TanStack React Query
- Client axios préconfiguré

### 4. Utiliser dans le code
```typescript
// Avant (stubs):
import { ObjectsService } from '@lepton/api-client'
ObjectsService.getObjects()  // ❌ Jamais appelé, 404

// Après (généré):
import { useGetObjects, useUpdateObject } from '@lepton/api'

function MyComponent() {
  const { data } = useGetObjects()  // ✅ Typé, avec autocomplete
  const mutation = useUpdateObject()
  
  return ...
}
```

## Commandes utiles

```bash
# Vérifier la compilation TypeScript
npm run typecheck

# Générer et vérifier
python scripts/export_openapi.py && bash scripts/generate_api_client.sh && npm run typecheck

# Builder pour production
npm run build
```

## Structure générée

```
src/api/generated/
├── client.ts              # Client axios préconfiguré
├── types/
│   ├── models.ts          # Types Pydantic → TypeScript
│   └── responses.ts       # Types de réponses
├── services/
│   ├── ObjectsService.ts
│   ├── SessionService.ts
│   └── ...
└── queries/               # TanStack React Query hooks
    ├── useGetObjects.ts
    ├── useUpdateObject.ts
    └── ...
```

## Important ⚠️

1. **Ne pas éditer** `src/api/generated/` - Regénérer à chaque changement API
2. **Ajouter au .gitignore**: `src/api/generated/` est généré, pas sourcé
3. **Export régulièrement**: Après chaque changement dans `snapserve/`

## Troubleshooting

### "openapi.json not found"
→ Exécuter: `python scripts/export_openapi.py`

### "Module @lepton/api not found"
→ Regénérer: `bash scripts/generate_api_client.sh`

### TypeScript errors après génération
→ Vérifier: `npm run typecheck`

## Prochaines phases

- **P2**: Intégrer les queries générées dans SessionContext
- **P3**: Utiliser les types pour validation backend
- **P4**: Collaboratif avec mutation scopes par ID
