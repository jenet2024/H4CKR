import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";

type RegisterData = {
    pseudo: string;
    email: string;
    password: string;
};

export default function RegisterForm() {
    const [form, setForm] = useState<RegisterData>({
        pseudo: "",
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
            const response = await fetch("http://127.0.0.1:8000/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(form),
            });

            const data = await response.json();

            console.log("Response data:", data);
            console.log("Response status:", response.status);
            if (!response.ok) {
                setMessage(typeof data.detail === "string" ? data.detail : "Erreur d'inscription");
                return;
            }

            setMessage("Inscription réussie");
            console.log(data);
        } catch (error) {
            console.error("Erreur réseau :", error);
            setMessage("Serveur inaccessible");
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                name="pseudo"
                placeholder="Nom d'utilisateur"
                value={form.pseudo}
                onChange={handleChange}
            />

            <input
                type="email"
                name="email"
                placeholder="Email"
                value={form.email}
                onChange={handleChange}
            />

            <input
                type="password"
                name="password"
                placeholder="Mot de passe"
                value={form.password}
                onChange={handleChange}
            />

            <button type="submit">S'inscrire</button>

            {message !== "" && <p>{message}</p>}
        </form>
    );
}