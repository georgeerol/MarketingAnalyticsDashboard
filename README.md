# shadcn/ui monorepo template

## Requirements

### Part 1: User Management
1. Implement user authentication
2. Implement a user dashboard

### Part 2: Google Meridian MMM Dashboard  
3. Load and integrate the Google Meridian model trace (`saved_mmm.pkl`)
4. Create contribution charts (pick one type)
5. Implement response curves showing diminishing returns
6. Build compelling customer narrative for channel performance

### Reference Documentation
- [Google Meridian Developer Documentation](https://developers.google.com/meridian/docs/advanced-modeling/interpret-visualizations)





## General structure
- apps
    - api: fastapi
    - web: nextjs frontend
- packages
    - ui: shadcn component library
    - docker: dockerized database setup 

## Getting started
Use the monorepo setup. 

**Install dependencies:**
```bash
pnpm install
```

**Start development:**
```bash
pnpm dev
```

This will:
- Install dependencies for all apps and packages
- Spin up docker-compose /packages/docker
    - 5432 for database
    - 8080 for adminer (db ui)
- Start fastapi dev server
- Start next application in dev
 

## Frontend component library
### Usage

```bash
pnpm dlx shadcn@latest init
```

### Adding components

To add components to your app, run the following command at the root of your `web` app:

```bash
pnpm dlx shadcn@latest add button -c apps/web
```

This will place the ui components in the `packages/ui/src/components` directory.

### Tailwind

Your `tailwind.config.ts` and `globals.css` are already set up to use the components from the `ui` package.

### Using components

To use the components in your app, import them from the `ui` package.

```tsx
import { Button } from "@workspace/ui/components/button"
```



