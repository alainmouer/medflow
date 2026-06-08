export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-sky-600">MedFlow</h1>
      <p className="mt-4 text-lg text-slate-600">Plateforme medicale intelligente — Version Initiale</p>
      <div className="mt-8 flex gap-4">
        <a href="/login" className="rounded-md bg-sky-600 px-4 py-2 text-white hover:bg-sky-700">
          Connexion
        </a>
        <a href="/dashboard" className="rounded-md border border-sky-600 px-4 py-2 text-sky-600 hover:bg-sky-50">
          Tableau de bord
        </a>
      </div>
    </main>
  );
}
