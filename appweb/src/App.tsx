import { useState } from "react";
import { type Lang, translations } from "./config/translations.ts";
import Navbar from "./Navbar.tsx";
import Hero from "./Hero.tsx";
import Footer from "./Footer.tsx";
import "./App.css";
import RegisterForm from "./components/RegisterForm.tsx";
import LoginForm from "./components/LoginForm.tsx";

export default function App() {
  const [lang, setLang] = useState<Lang>("fr");
  const t = translations[lang];

  const handleDownload = () => {
    alert("Téléchargement de H4CHR.exe...");
  };
  

  return (
    <div className="app">
      <div className="scanline-wrap" aria-hidden="true">
        <div className="scanline-beam" />
        <div className="crt-lines" />
      </div>
      <Navbar lang={lang} setLang={setLang} t={t} onDownload={handleDownload} />
      <main>
        <Hero t={t} onDownload={handleDownload} />
        <RegisterForm />
        <LoginForm/>
      </main>
      <Footer t={t} />
    </div>
  );
}