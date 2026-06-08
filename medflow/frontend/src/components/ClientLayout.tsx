"use client";

import { I18nextProvider } from "react-i18next";
import i18n from "@/i18n";
import NavBar from "./NavBar";
import CommandPalette from "./CommandPalette";

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <I18nextProvider i18n={i18n}>
      <NavBar />
      <CommandPalette />
      {children}
    </I18nextProvider>
  );
}
