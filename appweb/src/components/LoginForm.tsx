import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

// On définit les données nécessaires pour la connexion
type LoginData = {
    email: string;
    password: string;
};

export default function LoginForm() {
    const [form, setForm] = useState<LoginData>({
        email: "",
        password: "",
    });

    const [message, setMessage] = useState<string>("");

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;

        setForm((prev) => ({
            ...prev,
            [name]: value,
        }));
    };

    const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        try {
            // Mise à jour de l'URL vers /login
            const response = await fetch("http://127.0.0.1:8000/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(form),
            });

            const data = await response.json();

            if (!response.ok) {
                // Affiche l'erreur venant du backend (ex: "Identifiants invalides")
                setMessage(typeof data.detail === "string" ? data.detail : "Erreur de connexion");
                return;
            }

            // Ici, vous recevrez probablement un Token (JWT)
            setMessage("Connexion réussie !");
            console.log("Token reçu :", data.access_token);
            
            // Note : Vous devriez ici stocker le token (localStorage ou Cookie) 
            // et rediriger l'utilisateur vers une page protégée.
            
        } catch (error) {
            console.error("Erreur réseau :", error);
            setMessage("Serveur inaccessible");
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>Connexion</h2>
            
            <input
                type="email"
                name="email"
                placeholder="Email"
                required
                value={form.email}
                onChange={handleChange}
            />

            <input
                type="password"
                name="password"
                placeholder="Mot de passe"
                required
                value={form.password}
                onChange={handleChange}
            />

            <button type="submit">Se connecter</button>

            {message !== "" && <p style={{ color: message.includes("réussie") ? "green" : "red" }}>{message}</p>}
        </form>
    );
}