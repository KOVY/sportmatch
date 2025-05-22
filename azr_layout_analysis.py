#!/usr/bin/env python3
# coding: utf-8

from azr.absolute_zero_reasoner import AbsoluteZeroReasoner

# Inicializace AZR
azr = AbsoluteZeroReasoner()

# Vytvořit konkrétní dotaz na optimalizaci layoutů
query = """
# SportMatch: Optimalizace hierarchie layoutů pro eliminaci duplicit

## Kontext problému
V aplikaci SportMatch máme aktuálně několik layoutů, které způsobují duplicitní vykreslování komponent:

1. AppLayout - hlavní layout s Navbar, Footer a BottomNav
2. CzechLayout - specifický layout pro české stránky
3. EnglishLayout - specifický layout pro anglické stránky
4. SportLayout - specializovaný layout pro sportovní stránky s SportNavbar

Problémem je, že tyto layouty jsou vloženy do sebe (např. `<AppLayout><CzechLayout><SportLayout>...</SportLayout></CzechLayout></AppLayout>`), což způsobuje, že se některé komponenty jako Navbar a Footer vykreslují vícekrát.

## Aktuální implementace layoutů

**AppLayout.tsx**:
```tsx
export function AppLayout({ children }: { children: React.ReactNode }) {
  // ...
  return (
    <ContrastProvider>
      <GlobalTeamColorApplier />
      <div className="flex flex-col min-h-screen bg-background">
        {!isSocialHub && <Navbar />}
        <main className="flex-1 overflow-y-auto">
          <AnimatePresence mode="popLayout">
            <div key="main-content">{children}</div>
          </AnimatePresence>
        </main>
        {!hideFooter && !isSocialHub && (
          <div className="hidden md:block"><Footer /></div>
        )}
        {!isSocialHub && (
          <motion.div className="fixed bottom-0 left-0 right-0 z-50 md:hidden">
            <BottomNav />
          </motion.div>
        )}
      </div>
    </ContrastProvider>
  );
}
```

**SportLayout.tsx**:
```tsx
export function SportLayout({ children }: SportLayoutProps) {
  // ...
  return (
    <ContrastProvider>
      <GlobalTeamColorApplier />
      <div className="flex flex-col min-h-screen bg-background">
        {currentSport.name && (
          <SportNavbar sportName={currentSport.name} sportColor={currentSport.color} />
        )}
        <main className="flex-1 overflow-y-auto">
          <AnimatePresence mode="popLayout">
            <div key="main-content">{children}</div>
          </AnimatePresence>
        </main>
      </div>
    </ContrastProvider>
  );
}
```

**CzechLayout.tsx** (po nedávné úpravě):
```tsx
const CzechLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // ...
  return (
    <div className="czech-layout">
      <main>
        {children}
      </main>
    </div>
  );
};
```

**EnglishLayout.tsx** (po nedávné úpravě):
```tsx
const EnglishLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // ...
  return (
    <div className="english-layout">
      <main>
        {children}
      </main>
    </div>
  );
};
```

## Použití v aplikaci:

```tsx
// Příklad pro českou sportovní stránku
<AppLayout>
  <CzechLayout>
    <SportLayout>
      <TenisPage />
    </SportLayout>
  </CzechLayout>
</AppLayout>
```

## Otázky
1. Jaká je ideální hierarchie layoutů, aby se eliminovalo duplicitní vykreslování?
2. Jak správně řešit SportLayout, který má vlastní navigaci (SportNavbar)?
3. Jakou konkrétní strukturu layoutů v React komponentách bys navrhl/a?
4. Jak elegantně řešit jazykové varianty bez duplicitního kódu?
5. Jak spojit specializované layouty (např. pro streamy) s vícejazyčností?
"""

# Analýza pomocí AZR
result = azr.reason(query)

# Vypsat odpověď
print("=" * 50)
print("ODPOVĚĎ AZR:")
print("=" * 50)
print(result["answer"])