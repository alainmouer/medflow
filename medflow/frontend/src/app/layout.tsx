import "./globals.css";
import NavBar from "@/components/NavBar";

export const metadata = {
  title: "MedFlow",
  description: "Plateforme medicale intelligente",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className="min-h-screen bg-white text-slate-900">
        <NavBar />
        {children}
      </body>
    </html>
  );
}
