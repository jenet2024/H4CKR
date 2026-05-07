"""
Seeder — insère les niveaux, énigmes et badges initiaux.
Lance avec : python -m database.seeder
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import SessionLocal, init_db
from models.level import Level, Enigma
from models.user import User
from game.enigma_engine import hash_answer
from game.badge_engine import seed_badges
from auth.security import hash_password


def seed():
    init_db()
    db = SessionLocal()

    # ── Badges ────────────────────────────────────────────────────────────────
    seed_badges(db)
    print("✅ Badges insérés")

    # ── Admin par défaut ──────────────────────────────────────────────────────
    if not db.query(User).filter(User.email == "admin@h4ckr.local").first():
        admin = User(
            pseudo="Admin",
            email="admin@h4ckr.local",
            hashed_password=hash_password("Admin1234!"),
            is_admin=True,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        print("✅ Admin créé (admin@h4ckr.local / Admin1234!)")

    # ── Niveau 1 : Débutant ───────────────────────────────────────────────────
    if not db.query(Level).filter(Level.slug == "beginner").first():
        level1 = Level(
            slug="beginner",
            name="Niveau 1 — Débutant",
            description=(
                "Bienvenue Agent. Votre première mission commence ici. "
                "Vous allez apprendre les bases du hacking éthique : "
                "décodage, stéganographie et analyse de fichiers."
            ),
            order=1,
            video_file="level1_intro.mp4",
            max_points=500,
        )
        db.add(level1)
        db.flush()

        enigmas_beginner = [
            Enigma(
                level_id=level1.id,
                slug="base64_message",
                title="Message Mystérieux",
                description=(
                    "Vous avez intercepté ce message encodé :\n\n"
                    "SGVsbG8gQWdlbnQgISBMZSBtb3QgZGUgcGFzc2UgZXN0IDogSEFDS0VSMjAyNQ==\n\n"
                    "Décodez-le et entrez le mot de passe trouvé."
                ),
                type="base64",
                hint1="Ce format d'encodage utilise les caractères A-Z, a-z, 0-9, +, /",
                hint2="Cherchez un outil en ligne 'Base64 decode' ou utilisez Python : base64.b64decode()",
                hint3="La réponse est : HACKER2025",
                answer_hash=hash_answer("HACKER2025"),
                points=100,
                order=1,
            ),
            Enigma(
                level_id=level1.id,
                slug="caesar_cipher",
                title="Le Chiffre de César",
                description=(
                    "Le message suivant a été chiffré avec un décalage de 13 (ROT13) :\n\n"
                    "UNPXRE_QROHGNAG\n\n"
                    "Déchiffrez ce message et entrez la réponse en majuscules."
                ),
                type="caesar",
                hint1="ROT13 signifie que chaque lettre est décalée de 13 positions dans l'alphabet.",
                hint2="A devient N, B devient O, H devient U, U devient H...",
                hint3="La réponse est : HACKER_DEBUTANT",
                answer_hash=hash_answer("HACKER_DEBUTANT"),
                points=100,
                order=2,
            ),
            Enigma(
                level_id=level1.id,
                slug="stegano_image",
                title="Image Suspecte",
                description=(
                    "Un fichier image a été envoyé par un agent suspect.\n"
                    "Téléchargez le fichier 'suspect.png' et examinez ses métadonnées.\n\n"
                    "Quel est le commentaire caché dans les métadonnées ?"
                ),
                type="stegano",
                file_path="enigmas/suspect.png",
                hint1="Les images contiennent des données EXIF invisibles à l'œil nu.",
                hint2="Utilisez un outil comme ExifTool ou consultez les propriétés du fichier.",
                hint3="Le commentaire caché est : GHOST_PROTOCOL",
                answer_hash=hash_answer("GHOST_PROTOCOL"),
                points=150,
                order=3,
            ),
            Enigma(
                level_id=level1.id,
                slug="audio_message",
                title="Signal Audio Étrange",
                description=(
                    "Nos services ont intercepté un fichier audio suspect : 'signal.wav'.\n"
                    "Écoutez-le attentivement. Un message est caché dans le signal.\n\n"
                    "Quel mot est prononcé à l'envers dans l'enregistrement ?"
                ),
                type="audio",
                file_path="enigmas/signal.wav",
                hint1="Importez le fichier dans Audacity (gratuit) et retournez la piste.",
                hint2="Le message est court — un seul mot prononcé à l'envers.",
                hint3="Le mot à l'envers est : INFILTRE",
                answer_hash=hash_answer("INFILTRE"),
                points=150,
                order=4,
            ),
        ]
        db.add_all(enigmas_beginner)
        db.commit()
        print(f"✅ Niveau Débutant créé avec {len(enigmas_beginner)} énigmes")

    # ── Niveau 2 : Expert ─────────────────────────────────────────────────────
    if not db.query(Level).filter(Level.slug == "expert").first():
        level2 = Level(
            slug="expert",
            name="Niveau 2 — Expert",
            description=(
                "Agent, vous avez prouvé vos capacités. "
                "Vous accédez maintenant aux missions de niveau expert. "
                "Terminal actif, contre-mesures en place. Bonne chance."
            ),
            order=2,
            video_file="level2_intro.mp4",
            max_points=1000,
        )
        db.add(level2)
        db.flush()

        enigmas_expert = [
            Enigma(
                level_id=level2.id,
                slug="log_analysis",
                title="Analyse de Logs Serveur",
                description=(
                    "Téléchargez le fichier 'logs_serveur.txt'.\n"
                    "Un intrus s'est connecté au serveur cette nuit.\n\n"
                    "Trouvez l'adresse IP de l'intrus."
                ),
                type="logs",
                file_path="enigmas/logs_serveur.txt",
                hint1="Cherchez les lignes contenant 'ERROR' ou 'Intrusion'.",
                hint2="Les logs enregistrent l'IP source de chaque connexion.",
                hint3="L'IP est : 192.168.42.13",
                answer_hash=hash_answer("192.168.42.13"),
                points=150,
                order=1,
            ),
            Enigma(
                level_id=level2.id,
                slug="terminal_ssh",
                title="Connexion SSH Compromise",
                description=(
                    "Utilisez le terminal pour analyser le système.\n"
                    "Commencez par : scan 192.168.1.1\n"
                    "Puis analysez les logs pour trouver le nom d'utilisateur "
                    "qui a réussi à se connecter frauduleusement."
                ),
                type="terminal",
                hint1="Tapez 'help' dans le terminal pour voir les commandes disponibles.",
                hint2="La commande 'cat logs_serveur.txt' affiche les logs.",
                hint3="L'utilisateur est : s3cur1ty_t3am",
                answer_hash=hash_answer("s3cur1ty_t3am"),
                points=200,
                order=2,
            ),
            Enigma(
                level_id=level2.id,
                slug="metadata_extraction",
                title="Extraction de Métadonnées",
                description=(
                    "Un fichier image nommé 'suspect_expert.png' a été trouvé "
                    "sur le serveur compromis.\n\n"
                    "Extrayez les métadonnées et trouvez le mot de passe caché "
                    "dans le champ 'Comment'."
                ),
                type="metadata",
                file_path="enigmas/suspect_expert.png",
                hint1="Utilisez ExifTool : exiftool suspect_expert.png",
                hint2="Ou dans le terminal du jeu : extract suspect_expert.png",
                hint3="Le mot de passe est : p4ssw0rd_h1dd3n_h3r3",
                answer_hash=hash_answer("p4ssw0rd_h1dd3n_h3r3"),
                points=200,
                order=3,
            ),
            Enigma(
                level_id=level2.id,
                slug="base64_terminal",
                title="Message Chiffré dans le Terminal",
                description=(
                    "Dans le terminal, affichez le fichier 'message_chiffre.b64'.\n"
                    "Décodez le contenu Base64 pour trouver le mot de passe final.\n\n"
                    "Entrez le mot de passe trouvé après décodage."
                ),
                type="base64",
                hint1="Commande : cat message_chiffre.b64 puis decode <contenu>",
                hint2="Le contenu Base64 commence par 'SGVs...'",
                hint3="Le message décodé contient : HACKER2025",
                answer_hash=hash_answer("HACKER2025"),
                points=200,
                order=4,
            ),
            Enigma(
                level_id=level2.id,
                slug="final_mission",
                title="Mission Finale — Clé de Chiffrement",
                description=(
                    "Vous avez tous les éléments. La clé finale est construite "
                    "à partir de vos découvertes :\n\n"
                    "[ IP_intrus ]_[ user_compromis ]_[ pass_metadata ]\n\n"
                    "Assemblez les 3 éléments trouvés précédemment (séparés par _) "
                    "pour former la clé finale."
                ),
                type="terminal",
                hint1="Les 3 éléments sont dans les énigmes précédentes.",
                hint2="Format : IP_user_password (tout en minuscules)",
                hint3="La clé est : 192.168.42.13_s3cur1ty_t3am_p4ssw0rd_h1dd3n_h3r3",
                answer_hash=hash_answer("192.168.42.13_s3cur1ty_t3am_p4ssw0rd_h1dd3n_h3r3"),
                points=250,
                order=5,
            ),
        ]
        db.add_all(enigmas_expert)
        db.commit()
        print(f"✅ Niveau Expert créé avec {len(enigmas_expert)} énigmes")

    db.close()
    print("\n🎮 Base de données initialisée avec succès !")
    print("   Niveaux : Débutant (4 énigmes) + Expert (5 énigmes)")
    print("   Badges  : 10 badges disponibles")


if __name__ == "__main__":
    seed()
