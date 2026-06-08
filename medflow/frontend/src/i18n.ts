"use client";

import { createInstance } from "i18next";
import { initReactI18next } from "react-i18next";

const resources = {
  fr: {
    common: {
      dashboard: "Tableau de bord",
      patients: "Patients",
      agenda: "Agenda",
      triage: "Triage",
      billing: "Facturation",
      admin: "Admin",
      login: "Connexion",
      logout: "Deconnexion",
      save: "Enregistrer",
      cancel: "Annuler",
      create: "Créer",
      edit: "Modifier",
      delete: "Supprimer",
      search: "Rechercher",
      loading: "Chargement...",
      noData: "Aucune donnée",
      welcome: "Bienvenue sur MedFlow",
    },
    medical: {
      episode: "Épisode",
      prescription: "Ordonnance",
      analysis: "Analyse IA",
      vitalSigns: "Signes vitaux",
      chiefComplaint: "Motif principal",
    },
  },
  en: {
    common: {
      dashboard: "Dashboard",
      patients: "Patients",
      agenda: "Agenda",
      triage: "Triage",
      billing: "Billing",
      admin: "Admin",
      login: "Login",
      logout: "Logout",
      save: "Save",
      cancel: "Cancel",
      create: "Create",
      edit: "Edit",
      delete: "Delete",
      search: "Search",
      loading: "Loading...",
      noData: "No data",
      welcome: "Welcome to MedFlow",
    },
    medical: {
      episode: "Episode",
      prescription: "Prescription",
      analysis: "AI Analysis",
      vitalSigns: "Vital Signs",
      chiefComplaint: "Chief Complaint",
    },
  },
};

const i18n = createInstance();
i18n.use(initReactI18next).init({
  resources,
  lng: "fr",
  fallbackLng: "fr",
  defaultNS: "common",
  interpolation: { escapeValue: false },
});

export default i18n;
