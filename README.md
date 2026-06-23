# Etape 1

Prompt 1 
"content": "Explique le RAG en une phrase."
uv run etape1.py
Le rôle des agences d'influence et de publicité (RAG) est un concept qui désigne les entreprises qui utilisent la publicité sur internet pour promouvoir et créer du buzz autour de produits ou de marques en ligne.

Prompt 2
"content": "Donne 3 idées de noms d'app."
 uv run etape1.py
Voici trois idées pour un nom d'application :
1. **AppLynx** : Ce nom est court et facile à retenir, il suggère une application liée au monde des réseaux (lynx).
2. **MonDiary** : Cette app peut être dédiée à la gestion de l'alimentation, parexemple.
3. **Journify** : Ce nom s'inspire de la racine "jour" et suggère une application liée aux agendas, à la planification quotidienne.

# Etape 2
{"role": "system", "content":
"Tu es un assistant qui répond en français, de façon claire et brève. "
"Si tu ne sais pas, dis-le honnêtement."},
{"role": "user", "content": "Qu'est-ce qu'une base de données ?"}

uv run etape2.py
Une base de données est un ensemble organisé d'informations numériques stockées dans une structure déterminée pour les gérer, les sauvegarder et les consulter facilement. Cela peut être des textes, des chiffres, des images, etc.

Il existe plusieurs types de bases de données : relationnelles (comme MySQL ou Microsoft SQL), NoSQL (par exemple MongoDB), documentaires, graphiques, etc. Chaque type a sa propre manière d'organiser et de manipuler les données.

# Etape 3
uv run rag.py
Les cours se terminent à 17h.

uv run rag.py
Question: C'est quand la prochaine coupe du monde ?
Je ne sais pas. 